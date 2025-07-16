USE mytest;
GO

INSERT INTO Room (Id, Nom, Largeur, Longueur, Hauteur)
VALUES ('room-001', 'Assembly Room', 15.0, 10.0, 5.0);


INSERT INTO EquipmentType (Nom, Description)
VALUES 

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


-- Insert Equipment
INSERT INTO Equipment (Id, ParentEquipmentId, EquipmentTypeId, ManufacturerId, ModelId, RoomId, Nom, PrefabKey, SerialNumber, PurchaseDate)
VALUES 
('1', NULL, @Type, @Mfr, @Model, 'room-001', 'CNC Machine', 'CNC_Prefab', 'Test', '2023-02-15'),
('2', '1', @Type, @Mfr, @Model, 'room-001', 'CNC Bridge', 'CNC_Bridge_Prefab', 'Test', '2023-02-15'),
('3', NULL, @Type, @Mfr, @Model, 'room-001', 'Robot', 'Robot_Prefab', 'Test', '2023-02-15'),
('4', NULL, @TypeCNC_Structure, @Mfr, @Model, 'room-001', 'CNC_Structure', 'CNC_Structure', 'Test', '2025-07-11'),
('5', '8', @TypeCNC_Bridge, @Mfr, @Model, 'room-001', 'CNC_Bridge', NULL, 'Test', '2025-07-11'),
('6', '9', @TypeCNC_Rack, @Mfr, @Model, 'room-001', 'CNC_Rack', NULL, 'Test', '2025-07-11'),
('7', '10', @TypeCNC_Spindle, @Mfr, @Model, 'room-001', 'CNC_Spindle', NULL, 'Test', '2025-07-11');


-- Get Type IDs
DECLARE @TypeTemp INT = (SELECT Id FROM Type WHERE Nom = 'Temperature');
DECLARE @TypeStatus INT = (SELECT Id FROM Type WHERE Nom = 'Status');
DECLARE @TypeLoad INT = (SELECT Id FROM Type WHERE Nom = 'Load');

DECLARE @TypeSpeed INT = (SELECT Id FROM Type WHERE Nom = 'Speed');
DECLARE @TypeSuccion INT = (SELECT Id FROM Type WHERE Nom = 'Succion');


-- Temperature (float) for Equipment 1
INSERT INTO Variable (EquipmentId, Nom, DataItemId, TypeId)
VALUES ('1', 'test', 'test', @TypeTemp);
DECLARE @VarTemp INT = SCOPE_IDENTITY();

INSERT INTO Data (VariableId, Value)
VALUES (@VarTemp, '8');

INSERT INTO Data (VariableId, Value)
VALUES (@VarTemp, '10');

INSERT INTO Data (VariableId, Value)
VALUES (@VarTemp, '12');

-- Status (string) for Equipment 1
INSERT INTO Variable (EquipmentId, Nom, DataItemId, TypeId)
VALUES ('1', 'test', 'test', @TypeStatus);
DECLARE @VarStatus INT = SCOPE_IDENTITY();

INSERT INTO Data (VariableId, Value)
VALUES (@VarStatus, 'Operational');

-- Load (float) for Equipment 2
INSERT INTO Variable (EquipmentId, Nom, DataItemId, TypeId)
VALUES ('2', 'test', 'test', @TypeLoad);
DECLARE @VarLoad INT = SCOPE_IDENTITY();

INSERT INTO Data (VariableId, Value)
VALUES (@VarLoad, '120.5');


-- Succion state for Equipment 4
INSERT INTO Variable (EquipmentId, Nom, DataItemId, TypeId)
VALUES ('4', 'test', 'test', @TypeSuccion);
DECLARE @VarSuccion INT = SCOPE_IDENTITY();

INSERT INTO Data (VariableId, Value)
VALUES (@VarSuccion, 'false');

-- Succion state for Equipment 7
INSERT INTO Variable (EquipmentId, Nom, DataItemId, TypeId)
VALUES ('7', 'test', 'test', @TypeSpeed);
DECLARE @VarSpeed INT = SCOPE_IDENTITY();

INSERT INTO Data (VariableId, Value)
VALUES (@VarSpeed, 0);



-- -- Test CNC Machine
-- INSERT INTO Transform (EquipmentId, PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
-- VALUES ('1', 2.5, 0.0, 1.2, 0.0, 0.0, 0.0);

-- -- Test CNC Bridge
-- INSERT INTO Transform (EquipmentId, PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
-- VALUES ('2', 2.5, 1.5, 1.2, 0.0, 0.0, 0.0);

-- -- Test Robot
-- INSERT INTO Transform (EquipmentId, PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
-- VALUES ('3', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);

-- -- CNC_Structure
-- INSERT INTO Transform (EquipmentId, PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
-- VALUES ('8', 3.65, 0.8, 5.12, 0.0, 270, 0.0);

-- -- CNC_Bridge
-- INSERT INTO Transform (EquipmentId, PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
-- VALUES ('9', 5.0, -100.0, -1000.0, 0.0, 0.0, 0.0);

-- -- CNC_Rack
-- INSERT INTO Transform (EquipmentId, PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
-- VALUES ('10', -500.0, 575.0, -175.0, 0.0, 0.0, 0.0);

-- -- CNC_Spindle
-- INSERT INTO Transform (EquipmentId, PositionX, PositionY, PositionZ, RotationX, RotationY, RotationZ)
-- VALUES ('11', 0.0, -275.0, 240.0, 0.0, 0.0, 0.0);