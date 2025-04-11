package fr.matthieufouliard.model.Respond;

import java.util.UUID;

public class CreateGameRespond {
    public java.util.UUID UUID;

    public CreateGameRespond(UUID UUID) {
        this.UUID = UUID;
    }

    @Override
    public String toString() {
        return "{\n" +
                "UUID: " + this.UUID + "\n" +
                "}";
    }
}
