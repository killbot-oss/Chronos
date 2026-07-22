-- Seed data ported from the app's original local PHARMAS_DB / DOCTORS_DB_DEFAULT
-- arrays, so pharmacies/doctors tabs return real data immediately.
-- Run after schema.sql.

insert into pharmacies (name, address, phone, on_duty, lat, lon) values
('Pharmacie Rachel Yagma', 'YAGMA, Côté Est du Sanctuaire marial, voie YAGMA-KAMBOINSIN', '25407009', true, 12.4386, -1.60114),
('Pharmacie Elite', 'Avenue Yennega, route de Yagma', '25419177', true, 12.3985, -1.61269),
('Pharmacie Tenedia', 'Kamboinsin, après le 2iE en allant vers Pabré', '63930019', true, 12.4649, -1.55515),
('Pharmacie Barkwendé', 'Arrdt 8, Sect 35, face à la cité de Rimkièta', '25408590', true, 12.3737, -1.60851),
('Pharmacie Baowendsom', "Tampouy, nouveau goudron du collège Notre Dame de l'Espérance", '25414499', true, 12.4034, -1.57745),
('Pharmacie Crystal', "Kossoghin, face à la Mairie de l'Arrdt 9", '60460808', true, 12.4202, -1.55943),
('Pharmacie Pelega', 'Kilwin, Arrdt 3, Av. du Yatenga', '25350501', true, 12.3888, -1.57043),
('Pharmacie Tale', 'Route de Bobo, entre stations Total & Shell', '71620808', true, 12.3333, -1.60532),
('Pharmacie Monderou', 'Nonsin, face station OTAM, rue Karamogo', '25340528', true, 12.3761, -1.56373),
('Pharmacie Lanibougma', 'Tanghin, quartier Nonghin, non loin de la Station Radar', '25480797', true, 12.4157, -1.52381),
('Pharmacie Wend La Mita', "Sect 8, avenue du Yatenga, face école Kologh-Naba", '25341587', true, 12.3807, -1.54997),
('Pharmacie Wend La Lafi', 'Pissy, Route de Bobo, face station Shell de Pissy', '25431213', true, 12.3423, -1.57282),
('Pharmacie Maré', 'Gounghin, non loin du Stade du 4 Août', '', true, 12.3668, -1.55061),
('Pharmacie Desa', "Tanghin, non loin de l'Hôtel Ricardo", '25475050', true, 12.3914, -1.52927),
('Pharmacie Rivage', "Av. du Kadiogo, 200m Est de l'échangeur Ouest", '25341939', true, 12.3541, -1.55213),
('Pharmacie Rayib-Tiga', 'Av. Jean-Baptiste Ouédraogo, 800m Nord Clinique Notre-Dame-de-la-Paix', '65321153', true, 12.4074, -1.5077),
('Pharmacie Liberté', 'Dapoya, 60m station Shell cité An III', '25410131', true, 12.3777, -1.53159),
('Pharmacie Carrefour', 'Avenue Kadiogo, Bilbalogo', '25332310', true, 12.3679, -1.53092),
('Pharmacie Vénégré', 'Pissy', '25430587', true, 12.3345, -1.55753);

insert into doctors (name, specialty, specialty_label, address, phone, availability, hours, distance_km, avatar) values
('Dr. Aminata Ouédraogo', 'cardio', 'Cardiologue', 'Clinique du Cœur, Secteur 4 — Ouagadougou', '+226 25 36 xx xx', "Disponible aujourd'hui", 'Lun–Ven 8h–17h', 1.2, 'AO'),
('Dr. Ibrahim Sawadogo', 'endocrino', 'Diabétologue', 'CHU Yalgado, Bâtiment D — Ouagadougou', '+226 25 33 xx xx', 'Prochain RDV : jeudi', 'Mar & Jeu 9h–13h', 3.5, 'IS'),
('Dr. Fatou Diallo', 'generaliste', 'Médecin Traitant', 'Cabinet Santé Plus, Secteur 11', '+226 70 xx xx xx', "Disponible aujourd'hui", 'Lun–Sam 7h30–18h', 0.8, 'FD'),
('Dr. Pascal Kaboré', 'nephro', 'Néphrologue', 'Clinique Suka, Secteur 15', '+226 25 41 xx xx', 'Absent — urgences uniquement', 'Mer & Ven 10h–14h', 5.1, 'PK'),
('Dr. Sylvie Compaoré', 'pneumo', 'Pneumologue', 'Centre Médical Protestant, Pissy', '+226 25 38 xx xx', 'Disponible demain', 'Lun–Ven 8h–16h', 2.7, 'SC');
