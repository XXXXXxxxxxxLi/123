import java.util.HashMap;
import java.util.Map;

public class UserManager {
    private Map<String, User> users = new HashMap<>();

    public boolean register(String username, String password) {
        if (users.containsKey(username)) {
            return false;  // 用户名已存在
        }
        users.put(username, new User(username, password));
        return true;
    }

    public boolean login(String username, String password) {
        User user = users.get(username);
        return user != null && user.matchPassword(password);
    }
}
