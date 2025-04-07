package com.project.repository.entity;

import org.bson.codecs.pojo.annotations.BsonProperty;
import org.bson.types.ObjectId;

import io.quarkus.mongodb.panache.PanacheMongoEntity;
import io.quarkus.mongodb.panache.common.MongoEntity;

@MongoEntity(collection =  "memories")
public class Ram extends PanacheMongoEntity {
	public ObjectId id;
	public String name;
	public String price;
	@BsonProperty("Speed")
	public String speed;
	@BsonProperty("Price / GB")
	public String costGB;
	@BsonProperty("Modules")
	public String modules;
	@BsonProperty("Color")
	public String Color;
	@BsonProperty("First Word Latency")
	public String fwl;
	@BsonProperty("CAS Latency")
	public String cl;
	@BsonProperty("Power Consumption")
	public int powerConsumption;

	public Ram(){}

}
