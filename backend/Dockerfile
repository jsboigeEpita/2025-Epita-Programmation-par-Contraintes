FROM eclipse-temurin:17-jdk
WORKDIR /app

COPY target/quarkus-app/ ./

# Définir le point d'entrée
CMD ["java", "-jar", "quarkus-app/quarkus-run.jar"]