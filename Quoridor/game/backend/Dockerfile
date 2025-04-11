# Step 1: Building the application

FROM maven:3.9.9-eclipse-temurin-21-alpine AS builder
WORKDIR /build
COPY pom.xml .
COPY src ./src
RUN mvn package -Dquarkus.package.type=uber-jar


# Step 2: Execute the application

FROM openjdk:21 AS runner
COPY --from=builder /build/target/quoridor-1.0-SNAPSHOT-runner.jar /src/Quoridor.jar
WORKDIR /src
EXPOSE 8080
CMD ["java", "-jar", "Quoridor.jar"]