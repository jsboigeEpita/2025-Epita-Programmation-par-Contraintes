package fr.matthieufouliard.model.Respond;

import java.util.UUID;

public class CreateUserRespond {
    public UUID UUID;

    public CreateUserRespond(UUID UUID) {
        this.UUID = UUID;
    }

    @Override
    public String toString() {
        return "{\n" +
                "UUID: " + this.UUID + "\n" +
                "}";
    }
}
