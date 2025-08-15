import datetime
import json
import os
import traceback
from pathlib import Path
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import numpy as np
from dateutil import parser
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import hann
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

class KafkaProcessor:
    """
    KafkaProcessor class for handling Kafka messages and processing them.
    This class provides methods to produce and consume messages from Kafka topics.
    """

    def __init__(self, ksqlClient, bootstrap_servers, input_topic, output_topic, 
                plot_dir="spectrogram_plots"):
        """
        Initializes the KafkaProducer and KafkaConsumer.
        Args:
            bootstrap_servers (str): Comma-separated list of Kafka bootstrap servers.
            input_topic (str): The topic to consume time series data from.
            output_topic (str): The topic to produce spectrogram data to.
            log_file (str): Path to the log file for spectrogram data.
            plot_dir (str): Directory to save spectrogram plot images.
        """
        self.ksqlClient = ksqlClient
        self.bootstrap_servers = bootstrap_servers
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.plot_dir = plot_dir
        self.plot_counter = 0
        self.buffer = {'values': [], 'times': []}
        self.time_series_window_seconds = 20
        
        self.window_size = 48
        self.hop_length = self.window_size//2
        self.sampling_rate = 100.0
        
        self._create_plot_directory()
        self._setup_kafka()
    

    def safe_deserialize_value(self, x):
        """Safe value deserializer with multiple fallback strategies"""
        if x is None:
            return None
        
        try:
            return json.loads(x.decode('utf-8'))
        except UnicodeDecodeError:
            try:
                decoded = x.decode('utf-8', errors='replace')
                return json.loads(decoded)
            except json.JSONDecodeError:
                try:
                    return json.loads(x.decode('latin-1'))
                except:
                    return x.decode('utf-8', errors='ignore')
        except json.JSONDecodeError:
            try:
                return x.decode('utf-8', errors='replace')
            except:
                return str(x)
    
    def safe_deserialize_key(self, x):
        """Safe key deserializer"""
        if x is None:
            return None
        try:
            decoded = x.decode('utf-8', errors='replace')
            clean_key = decoded.split('\x00')[0] if '\x00' in decoded else decoded
            return ''.join(c for c in clean_key if c.isprintable()) if clean_key else 'unknown'
        except:
            return 'unknown'
    
    def _setup_kafka(self):
        """
        Sets up the Kafka producer and consumer.
        """
        self.consumer = KafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id="stft_processor_group",
            value_deserializer=self.safe_deserialize_value,
            key_deserializer=self.safe_deserialize_key,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            auto_commit_interval_ms=1000
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None,
            acks='all',
            retries=3
        )

    def interpolate_to_uniform_sampling(self, values, times):
        """
        Interpolate irregular time series to uniform sampling
        """
        print(f'Times:{times}')
        print(f'Values{values}')
        if len(values) < 2:
            return np.array([]), np.array([])
        
        time_value_pairs = list(zip(times, values))
        time_value_pairs.sort(key=lambda x: x[0])
        
        sorted_times, sorted_values = zip(*time_value_pairs)
        times = list(sorted_times)
        values = list(sorted_values)
        
        t_start, t_end = times[0], times[-1]
        duration = t_end - t_start
        
        if duration <= 0:
            return np.array([]), np.array([])
        
        cs = CubicSpline(times, values)
        self.time_series_window_seconds = t_end - t_start
        uniform_times = np.arange(t_start, t_end, 0.01)

        interpolated_values = cs(uniform_times)

        plt.plot(np.arange(t_start, t_end, 0.01) , interpolated_values)
        plt.xlabel("Time (s)")
        plt.ylabel("Displacement (µm)")
        plt.title("Displacement in time")
        filename = f"signal{self.plot_counter}.png"
        filepath = os.path.join('signal_plots', filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
    
        return interpolated_values

    def compute_stft(self, signal):
        """
        Compute Short-Time FFT of the signal
        """
        if len(signal) < self.window_size:
            print(f"Signal too short for STFT: {len(signal)} samples, need at least {self.window_size}")
            return None
        
        try:
            window = hann(self.window_size)
            
            stft = ShortTimeFFT(window, hop=self.hop_length, fs=self.sampling_rate)
            
            spectrogram = stft.spectrogram(signal)
            print(f'Spectrgram shape {spectrogram.shape}')
            
            frequencies = stft.f
            times = stft.t(len(signal))
            print(f'frequencies:{frequencies}')
            
            return {
                'spectrogram': spectrogram.tolist(),
                'spectrogram_shape': spectrogram.shape,
                'frequencies': frequencies.tolist(),
                'times': times.tolist(),
                'sampling_rate': self.sampling_rate,
                'window_size': self.window_size,
                'hop_length': self.hop_length,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error computing STFT : {e}")
            return None
        
    def _create_plot_directory(self):
        """Create directory for saving spectrogram plots"""
        Path(self.plot_dir).mkdir(parents=True, exist_ok=True)
        Path('signal_plots').mkdir(parents=True, exist_ok=True)
        print(f"Spectrogram plots will be saved to: {self.plot_dir}")

    def plot_spectrogram(self, spectrogram_data, sensor_key):
        """
        Generate and save a visual spectrogram plot using matplotlib
        """
        try:
            self.plot_counter += 1
            
            spectrogram = np.array(spectrogram_data['spectrogram'])
            frequencies = np.array(spectrogram_data['frequencies'])
            times = np.array(spectrogram_data['times'])
            timestamp = spectrogram_data['timestamp']
            
            plt.figure(figsize=(14, 10))
            
            im = plt.pcolormesh(times, frequencies, spectrogram, 
                            cmap='hot', shading='gouraud')
            
            cbar = plt.colorbar(im, label='Vibration Amplitude')
            cbar.ax.tick_params(labelsize=10)
            
            plt.xlabel('Time (seconds)', fontsize=12)
            plt.ylabel('Frequency (Hz)', fontsize=12)
            plt.title(f'Vibration Spectrogram - Sensor: {sensor_key}\n{timestamp}', fontsize=14, pad=20)
            
            max_freq = min(10, frequencies[-1])
            plt.ylim(0.1, max_freq)
            
            plt.tight_layout()
            plt.grid(True, alpha=0.3)
            
            filename = f"spectrogram_{sensor_key}_{self.plot_counter:04d}.png"
            filepath = os.path.join(self.plot_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"Saved vibration spectrogram plot: {filepath}")            
            return filepath
            
        except Exception as e:
            print('Error plotting spectrogram:{e}')
            print(traceback.format_exception(e))
            return None
        
    def log_spectrogram_data(self, spectrogram_data, sensor_key):
        """
        Log spectrogram data to file for testing
        """
        try:
            self.plot_spectrogram(spectrogram_data, sensor_key)
                    
        except Exception as e:
            print(f"Error logging spectrogram data: {e}")

    def buffer_and_process_data(self, values, times):
        """
        Buffer data and process when enough data is available
        """
        if (times == [0.0]) and len(self.buffer['times']) > 1:
            uniform_values = self.interpolate_to_uniform_sampling(
                self.buffer['values'],
                self.buffer['times']
            )
            
            stft_result = self.compute_stft(uniform_values)
            
            if stft_result:
                self.send_spectrogram_data(stft_result)
                self.log_spectrogram_data(stft_result, "WTVB01")

            self.buffer['values'] = []
            self.buffer['times'] = []

        self.buffer['times'] = times
        self.buffer['values'] = [float(v) for v in values]
        
       

    def send_spectrogram_data(self, spectrogram_data):
        """
        Send spectrogram data to output Kafka topic
        """
        try:
            message = {
                'key': 'WTVB01',
                'spectrogram_data': spectrogram_data['spectrogram']
            }
            
            self.producer.send(
                self.output_topic,
                key='WTVB01',
                value=message
            )
            self.producer.send(
                self.output_topic,
                key='WTVB01',
                value=spectrogram_data
            )
            self.producer.flush()
        except KafkaError as e:
            print(f"Error sending spectrogram data: {e}")

    def process_message(self, key, value):
        """
        Process incoming time series message
        """
        try:
            if 'VALUE_LIST' not in value or 'TIMESTAMPS' not in value:
                print(f"Invalid message format: {value}")
                return
                
            relative_timestamps = self.convert_to_relative_time(value['TIMESTAMPS'])
            
            displacements = []
            for v in value['VALUE_LIST']:
                displacements.append(1000*float(v))
            
            self.buffer_and_process_data(displacements, relative_timestamps)
            
        except Exception as e:
            print(traceback.format_exception(e))

    def convert_to_relative_time(self, timestamps):
        """Convert timestamp strings to relative time in seconds"""
        parsed_timestamps = [parser.parse(timestamp) for timestamp in timestamps]
        zero = parsed_timestamps[0]
        relative_timestamps = [(timestamp - zero).total_seconds() for timestamp in parsed_timestamps]
        return relative_timestamps
    
    def run_streaming_processing(self):
        """Main processing loop with real-time processing"""
        print(f"Starting STFT processor - Input: {self.input_topic}, Output: {self.output_topic}")
        
        try:
            for message in self.consumer:
                self.process_message(message.key, message.value)
                
        except KeyboardInterrupt:
            print("STFT Processor stopped by user")
        except Exception as e:
            print(f"Error in processing loop: {e}")
        finally:
            self.consumer.close()
            self.producer.close()
            print("STFT Processor closed")