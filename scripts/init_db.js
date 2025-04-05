const fs = require('fs');

// var cases = cat("/docker-entrypoint-initdb.d/case_data.json");

db.cases.insertMany(JSON.parse(fs.readFileSync("/docker-entrypoint-initdb.d/case_data.json")));
db.cpus.insertMany(JSON.parse(fs.readFileSync("/docker-entrypoint-initdb.d/cpu_data.json")));
db.cpu_coolers.insertMany(JSON.parse(fs.readFileSync("/docker-entrypoint-initdb.d/cpu-cooler_data.json")));
db.memories.insertMany(JSON.parse(fs.readFileSync("/docker-entrypoint-initdb.d/memory_data.json")));
db.motherboards.insertMany(JSON.parse(fs.readFileSync("/docker-entrypoint-initdb.d/motherboard_data.json")));
db.power_supplys.insertMany(JSON.parse(fs.readFileSync("/docker-entrypoint-initdb.d/power-supply_data.json")));
db.storage_devices.insertMany(JSON.parse(fs.readFileSync("/docker-entrypoint-initdb.d/storage-devices_data.json")));
db.video_cards.insertMany(JSON.parse(fs.readFileSync("/docker-entrypoint-initdb.d/video-card_data.json")));