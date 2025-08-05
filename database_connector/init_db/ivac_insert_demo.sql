USE mytest;
GO

INSERT INTO EquipmentType (Nom, Description)
VALUES 
('BlastGate', 'Component used in dust collection systems to control airflow by directing it to different locations.'),
('Spindle', 'Rotating axis of a CNC machine.'),
('Lathe', 'Machine tool for shaping materials.');

INSERT INTO Manufacturer (Nom, Description)
VALUES 
('Test', 'Test');

INSERT INTO Model (Nom, Description)
VALUES 
('Test', 'Test');

INSERT INTO Type (Nom, Description, SubType)
VALUES 
('EquipmentMode', 'An indication that a piece of equipment, or a subpart of a piece of equipment, is performing specific types of activities.', 'Powered');

INSERT INTO Type (Nom, Description)
VALUES 
('DoorState', 'The operational state of a DOOR type component or composition element.');

DECLARE @TypeSpindle INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Spindle');
DECLARE @TypeLathe INT = (SELECT Id FROM EquipmentType WHERE Nom = 'Lathe');
DECLARE @TypeGate INT = (SELECT Id FROM EquipmentType WHERE Nom = 'BlastGate');
DECLARE @Mfr INT = (SELECT Id FROM Manufacturer WHERE Nom = 'Test');
DECLARE @Model INT = (SELECT Id FROM Model WHERE Nom = 'Test');

INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('8', NULL, @TypeSpindle, @Mfr, @Model, 'room-001',  'SpindleA1', 'Spindle_Prefab', 'Test', '2025-07-11'),
('9', NULL, @TypeLathe, @Mfr, @Model, 'room-001', 'LatheA2', 'Lathe_Prefab', 'Test', '2025-07-11'),
('10', NULL, @TypeGate, @Mfr, @Model, 'room-001', 'A1BlastGate', 'A1BlastGate_Prefab', 'Test', '2025-07-11'),
('11', NULL, @TypeGate, @Mfr, @Model, 'room-001', 'A2BlastGate', 'A2BlastGate_Prefab', 'Test', '2025-07-11');

DECLARE @TypeToolStatus INT = (SELECT Id FROM Type WHERE Nom = 'EquipmentMode');
DECLARE @TypeGateStatus INT = (SELECT Id FROM Type WHERE Nom = 'DoorState');
DECLARE @TypePosition INT = (SELECT Id FROM Type WHERE Nom = 'Position');
DECLARE @TypeAngle INT = (SELECT Id FROM Type WHERE Nom = 'Angle');

--A1ToolPlus
INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1ToolStatus', @TypeToolStatus, '8');
DECLARE @VarA1ToolStatus INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA1ToolStatus, 'ON', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA1ToolStatus, 'IVAC', 'A1ToolPlus');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindlePositionX', @TypePosition, '8');
DECLARE @VarSpindlePosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindlePosX, 2.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindlePositionY', @TypePosition, '8');
DECLARE @VarSpindlePosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindlePosY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindlePositionZ', @TypePosition, '8');
DECLARE @VarSpindlePosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindlePosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindleAngleX', @TypeAngle, '8');
DECLARE @VarSpindleAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindleAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindleAngleY', @TypeAngle, '8');
DECLARE @VarSpindleAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindleAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('SpindleAngleZ', @TypeAngle, '8');
DECLARE @VarSpindleAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarSpindleAngleZ, 0.0, CURRENT_TIMESTAMP);

--A2ToolPlus
INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2ToolStatus', @TypeToolStatus, '9');
DECLARE @VarA2ToolStatus INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA2ToolStatus, 'OFF', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA2ToolStatus, 'IVAC', 'A2ToolPlus');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LathePositionX', @TypePosition, '9');
DECLARE @VarLathePosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLathePosX, 3.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LathePositionY', @TypePosition, '9');
DECLARE @VarLathePosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLathePosY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LathePositionZ', @TypePosition, '9');
DECLARE @VarLathePosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLathePosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LatheAngleX', @TypeAngle, '9');
DECLARE @VarLatheAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLatheAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LatheAngleY', @TypeAngle, '9');
DECLARE @VarLatheAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLatheAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('LatheAngleZ', @TypeAngle, '9');
DECLARE @VarLatheAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarLatheAngleZ, 0.0, CURRENT_TIMESTAMP);

--A1BlastGate
INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1BlastGateStatus', @TypeGateStatus, '10');
DECLARE @VarA1BlastGate INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA1BlastGate, 'OPEN', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA1BlastGate, 'IVAC', 'A1BlastGate');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1GatePositionX', @TypePosition, '10');
DECLARE @VarA1GatePosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA1GatePosX, 2.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1GatePositionY', @TypePosition, '10');
DECLARE @VarA1GatePosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA1GatePosY, 1.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1GatePositionZ', @TypePosition, '10');
DECLARE @VarA1GatePosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA1GatePosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1GateAngleX', @TypeAngle, '9');
DECLARE @VarA1GateAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA1GateAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1GateAngleY', @TypeAngle, '9');
DECLARE @VarA1GateAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA1GateAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1GateAngleZ', @TypeAngle, '9');
DECLARE @VarA1GateAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA1GateAngleZ, 0.0, CURRENT_TIMESTAMP);

--A2BlastGate
INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2BlastGateStatus', @TypeGateStatus, '11');
DECLARE @VarA2BlastGate INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA2BlastGate, 'CLOSED', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA2BlastGate, 'IVAC', 'A2BlastGate');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GatePositionX', @TypePosition, '11');
DECLARE @VarA2GatePosX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GatePosX, 2.5, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GatePositionY', @TypePosition, '11');
DECLARE @VarA2GatePosY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GatePosY, 1.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GatePositionZ', @TypePosition, '11');
DECLARE @VarA2GatePosZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GatePosZ, 1.2, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GateAngleX', @TypeAngle, '9');
DECLARE @VarA2GateAngleX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GateAngleX, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GateAngleY', @TypeAngle, '9');
DECLARE @VarA2GateAngleY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GateAngleY, 0.0, CURRENT_TIMESTAMP);

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2GateAngleZ', @TypeAngle, '9');
DECLARE @VarA2GateAngleZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value, Timestamp)
VALUES (@VarA2GateAngleZ, 0.0, CURRENT_TIMESTAMP);