FROM eclipse-temurin:17-jdk
WORKDIR /app

COPY target/quarkus-app/ ./

# Définir le point d'entrée
CMD ["java", "-jar", "quarkus-run.jar"]


#DockerFile to mvn install projec