USE mytest;
GO

INSERT INTO Room (Id, Nom, Largeur, Longueur, Hauteur)
VALUES ('room-001', 'Assembly Room', 15.0, 10.0, 5.0);


INSERT INTO EquipmentType (Nom, Description)
VALUES 
('Test', 'Test'),
('CNC_Structure', 'Test'),
('CNC_Bridge', 'Test'),
('CNC_Rack', 'Test'),
('CNC_Spindle', 'Test');

INSERT INTO Manufacturer (Nom, Description)
VALUES 
('Test', 'Test');


INSERT INTO Model (Nom, Description)
VALUES 
('Test', 'Test');


INSERT INTO Type (Nom, Description, Subtype)
VALUES 
('PositionX', 'Position on X axis', 'float'),
('PositionY', 'Position on Y axis', 'float'),
('PositionZ', 'Position on Z axis', 'float'),
('RotationX', 'Rotation on X axis', 'float'),
('RotationY', 'Rotation on Y axis', 'float'),
('RotationZ', 'Rotation on Z axis', 'float'),
('Temperature', 'Current temperature', 'float'),
('Status', 'Current status', 'string'),
('Load', 'Current load', 'float'),
('Speed', 'Current speed', 'float'),
('Succion', 'Current status of succion (True, False)', 'bool');
GO

-- Get lookup IDs
DECLARE @Type INT = (SELECT Id FROM EquipmentType WHERE Nom = 'Test');
DECLARE @TypeCNC_Structure INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Structure');
DECLARE @TypeCNC_Bridge INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Bridge');
DECLARE @TypeCNC_Rack INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Rack');
DECLARE @TypeCNC_Spindle INT = (SELECT Id FROM EquipmentType WHERE Nom = 'CNC_Spindle');

DECLARE @Mfr INT = (SELECT Id FROM Manufacturer WHERE Nom = 'Test');
DECLARE @Model INT = (SELECT Id FROM Model WHERE Nom = 'Test');

-- Insert Equipment in correct order (parents before children)
INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('1', NULL, @Type, @Mfr, @Model, 'room-001', 'CNC Machine', 'CNC_Prefab', 'Test', '2023-02-15'),
('3', NULL, @Type, @Mfr, @Model, 'room-001', 'Robot', 'Robot_Prefab', 'Test', '2023-02-15'),
('4', NULL, @TypeCNC_Structure, @Mfr, @Model, 'room-001', 'CNC_Structure', 'CNC_Structure', 'Test', '2025-07-11');

-- Insert child equipment that references parent equipment
INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('2', '1', @Type, @Mfr, @Model, 'room-001', 'CNC Bridge', 'CNC_Bridge_Prefab', 'Test', '2023-02-15'),
('5', '4', @TypeCNC_Bridge, @Mfr, @Model, 'room-001', 'CNC_Bridge', NULL, 'Test', '2025-07-11'),
('6', '5', @TypeCNC_Rack, @Mfr, @Model, 'room-001', 'CNC_Rack', NULL, 'Test', '2025-07-11'),
('7', '6', @TypeCNC_Spindle, @Mfr, @Model, 'room-001', 'CNC_Spindle', NULL, 'Test', '2025-07-11');

-- Get Type IDs
DECLARE @TypeTemp INT = (SELECT Id FROM Type WHERE Nom = 'Temperature');
DECLARE @TypeStatus INT = (SELECT Id FROM Type WHERE Nom = 'Status');
DECLARE @TypeLoad INT = (SELECT Id FROM Type WHERE Nom = 'Load');
DECLARE @TypeSpeed INT = (SELECT Id FROM Type WHERE Nom = 'Speed');
DECLARE @TypeSuccion INT = (SELECT Id FROM Type WHERE Nom = 'Succion');
DECLARE @TypePosX INT = (SELECT Id FROM Type WHERE Nom = 'PositionX');
DECLARE @TypePosY INT = (SELECT Id FROM Type WHERE Nom = 'PositionY');
DECLARE @TypePosZ INT = (SELECT Id FROM Type WHERE Nom = 'PositionZ');
DECLARE @TypeRotX INT = (SELECT Id FROM Type WHERE Nom = 'RotationX');
DECLARE @TypeRotY INT = (SELECT Id FROM Type WHERE Nom = 'RotationY');
DECLARE @TypeRotZ INT = (SELECT Id FROM Type WHERE Nom = 'RotationZ');

-- Temperature (float) for Equipment 1
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'test', @TypeTemp);
DECLARE @VarTemp INT = SCOPE_IDENTITY();

INSERT INTO IntValue (VariableId, Value)
VALUES (@VarTemp, 8);

INSERT INTO IntValue (VariableId, Value)
VALUES (@VarTemp, 10);

INSERT INTO IntValue (VariableId, Value)
VALUES (@VarTemp, 12);

-- Status (string) for Equipment 1
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'test', @TypeStatus);
DECLARE @VarStatus INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value)
VALUES (@VarStatus, 'Operational');

-- Load (float) for Equipment 2
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'test', @TypeLoad);
DECLARE @VarLoad INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@VarLoad, 120.5);

-- Succion state for Equipment 4
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'test', @TypeSuccion);
DECLARE @VarSuccion INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value)
VALUES (@VarSuccion, 'INACTIVE');

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarSuccion, 'CNC123', 'vacuum_status');

-- Speed for Equipment 7
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'test', @TypeSpeed);
DECLARE @VarSpeed INT = SCOPE_IDENTITY();

INSERT INTO IntValue (VariableId, Value)
VALUES (@VarSpeed, 0);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarSpeed, 'CNC123', 'spindle_speed');

-- CNC Machine Transform (Equipment 1)
INSERT INTO Variable (EquipmentId, Nom, TypeId) 
VALUES ('1', 'PositionX', @TypePosX);
DECLARE @Var1PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1PX, 2.5);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'PositionY', @TypePosY);
DECLARE @Var1PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1PY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'PositionZ', @TypePosZ);
DECLARE @Var1PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1PZ, 1.2);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'RotationX', @TypeRotX);
DECLARE @Var1RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'RotationY', @TypeRotY);
DECLARE @Var1RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('1', 'RotationZ', @TypeRotZ);
DECLARE @Var1RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var1RZ, 0.0);

-- CNC Bridge Transform (Equipment 2)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'PositionX', @TypePosX);
DECLARE @Var2PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2PX, 2.5);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'PositionY', @TypePosY);
DECLARE @Var2PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2PY, 1.5);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'PositionZ', @TypePosZ);
DECLARE @Var2PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2PZ, 1.2);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'RotationX', @TypeRotX);
DECLARE @Var2RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'RotationY', @TypeRotY);
DECLARE @Var2RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('2', 'RotationZ', @TypeRotZ);
DECLARE @Var2RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var2RZ, 0.0);

-- Robot Transform (Equipment 3)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'PositionX', @TypePosX);
DECLARE @Var3PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3PX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'PositionY', @TypePosY);
DECLARE @Var3PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3PY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'PositionZ', @TypePosZ);
DECLARE @Var3PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3PZ, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'RotationX', @TypeRotX);
DECLARE @Var3RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'RotationY', @TypeRotY);
DECLARE @Var3RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('3', 'RotationZ', @TypeRotZ);
DECLARE @Var3RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var3RZ, 0.0);

-- CNC_Structure Transform (Equipment 4)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'PositionX', @TypePosX);
DECLARE @Var4PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4PX, 3.65);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'PositionY', @TypePosY);
DECLARE @Var4PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4PY, 0.8);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'PositionZ', @TypePosZ);
DECLARE @Var4PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4PZ, 5.12);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'RotationX', @TypeRotX);
DECLARE @Var4RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'RotationY', @TypeRotY);
DECLARE @Var4RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4RY, 270.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('4', 'RotationZ', @TypeRotZ);
DECLARE @Var4RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var4RZ, 0.0);

-- CNC_Bridge Transform (Equipment 5)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'PositionX', @TypePosX);
DECLARE @Var5PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5PX, 5.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'PositionY', @TypePosY);
DECLARE @Var5PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5PY, -100.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'PositionZ', @TypePosZ);
DECLARE @Var5PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5PZ, -1000.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'RotationX', @TypeRotX);
DECLARE @Var5RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'RotationY', @TypeRotY);
DECLARE @Var5RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('5', 'RotationZ', @TypeRotZ);
DECLARE @Var5RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var5RZ, 0.0);

-- CNC_Rack Transform (Equipment 6)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'PositionX', @TypePosX);
DECLARE @Var6PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6PX, -500.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'PositionY', @TypePosY);
DECLARE @Var6PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6PY, 575.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'PositionZ', @TypePosZ);
DECLARE @Var6PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6PZ, -175.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'RotationX', @TypeRotX);
DECLARE @Var6RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'RotationY', @TypeRotY);
DECLARE @Var6RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('6', 'RotationZ', @TypeRotZ);
DECLARE @Var6RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var6RZ, 0.0);

-- CNC_Spindle Transform (Equipment 7)
INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'PositionX', @TypePosX);
DECLARE @Var7PX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7PX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'PositionY', @TypePosY);
DECLARE @Var7PY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7PY, -275.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'PositionZ', @TypePosZ);
DECLARE @Var7PZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7PZ, 240.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'RotationX', @TypeRotX);
DECLARE @Var7RX INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7RX, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'RotationY', @TypeRotY);
DECLARE @Var7RY INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7RY, 0.0);

INSERT INTO Variable (EquipmentId, Nom, TypeId)
VALUES ('7', 'RotationZ', @TypeRotZ);
DECLARE @Var7RZ INT = SCOPE_IDENTITY();

INSERT INTO FloatValue (VariableId, Value)
VALUES (@Var7RZ, 0.0);