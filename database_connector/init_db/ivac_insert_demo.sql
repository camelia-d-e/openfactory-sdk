USE mytest;
GO

INSERT INTO Room (Id, Nom, Largeur, Longueur, Hauteur)
VALUES ('room-001', 'Assembly Room', 15.0, 10.0, 5.0);

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
('EquipmentMode', 'Current status of Tool (ON, OFF, or UNAVAILABLE)', 'Powered');

INSERT INTO Type (Nom, Description)
VALUES 
('DoorState', 'Current status  of Gate or Door(OPEN or CLOSED)');

INSERT INTO Transform (PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
VALUES (2.5, 0.0, 1.2, 0.0, 0.0, 0.0);

INSERT INTO Transform (PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
VALUES (3.5, 0.0, 1.2, 0.0, 0.0, 0.0);

INSERT INTO Transform (PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
VALUES (2.5, 1.0, 1.2, 0.0, 0.0, 0.0);

INSERT INTO Transform (PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
VALUES (3.5, 1.0, 1.2, 0.0, 0.0, 0.0);

GO

DECLARE @TypeSpindle INT = (SELECT Id FROM EquipmentType WHERE Nom = 'Spindle');
DECLARE @TypeLathe INT = (SELECT Id FROM EquipmentType WHERE Nom = 'Lathe');
DECLARE @TypeGate INT = (SELECT Id FROM EquipmentType WHERE Nom = 'BlastGate');
DECLARE @Mfr INT = (SELECT Id FROM Manufacturer WHERE Nom = 'Test');
DECLARE @Model INT = (SELECT Id FROM Model WHERE Nom = 'Test');

DECLARE @TransformId1 INT = (SELECT Id FROM Transform WHERE PositionX = 2.5 AND PositionY = 0.0 AND PositionZ = 1.2);
DECLARE @TransformId2 INT = (SELECT Id FROM Transform WHERE PositionX = 3.5 AND PositionY = 0.0 AND PositionZ = 1.2);
DECLARE @TransformId3 INT = (SELECT Id FROM Transform WHERE PositionX = 2.5 AND PositionY = 1.0 AND PositionZ = 1.2);
DECLARE @TransformId4 INT = (SELECT Id FROM Transform WHERE PositionX = 3.5 AND PositionY = 1.0 AND PositionZ = 1.2);

INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, TransformId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('1', NULL, @TypeSpindle, @Mfr, @Model, 'room-001', @TransformId1, 'SpindleA1', 'Spindle_Prefab', 'Test', '2025-07-11'),
('2', NULL, @TypeLathe, @Mfr, @Model, 'room-001', @TransformId2, 'LatheA2', 'Lathe_Prefab', 'Test', '2025-07-11'),
('3', NULL, @TypeGate, @Mfr, @Model, 'room-001', @TransformId3, 'A1BlastGate', 'A1BlastGate_Prefab', 'Test', '2025-07-11'),
('4', NULL, @TypeGate, @Mfr, @Model, 'room-001', @TransformId4, 'A2BlastGate', 'A2BlastGate_Prefab', 'Test', '2025-07-11');

GO

DECLARE @TypeToolStatus INT = (SELECT Id FROM Type WHERE Nom = 'EquipmentMode');
DECLARE @TypeGateStatus INT = (SELECT Id FROM Type WHERE Nom = 'DoorState');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1ToolStatus', @TypeToolStatus, '1');
DECLARE @VarA1ToolStatus INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA1ToolStatus, 'ON', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA1ToolStatus, 'IVAC', 'A1ToolPlus');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2ToolStatus', @TypeToolStatus, '2');
DECLARE @VarA2ToolStatus INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA2ToolStatus, 'OFF', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA2ToolStatus, 'IVAC', 'A2ToolPlus');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A1BlastGateStatus', @TypeGateStatus, '3');
DECLARE @VarA1BlastGate INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA1BlastGate, 'OPEN', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA1BlastGate, 'IVAC', 'A1BlastGate');

INSERT INTO Variable (Nom, TypeId, EquipmentId)
VALUES ('A2BlastGateStatus', @TypeGateStatus, '4');
DECLARE @VarA2BlastGate INT = SCOPE_IDENTITY();

INSERT INTO StrValue (VariableId, Value, Timestamp)
VALUES (@VarA2BlastGate, 'CLOSED', CURRENT_TIMESTAMP);

INSERT INTO OpenFactoryLink (VariableId, AssetUuid, DataItemId)
VALUES (@VarA2BlastGate, 'IVAC', 'A2BlastGate');