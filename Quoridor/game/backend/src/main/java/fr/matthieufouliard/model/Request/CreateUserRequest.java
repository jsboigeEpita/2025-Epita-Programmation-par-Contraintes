package fr.matthieufouliard.model.Request;

public class CreateUserRequest {
    public String username;

    @Override
    public String toString() {
        return "{\n" +
                "username: " + this.username + "\n" +
                "}";
    }
}
