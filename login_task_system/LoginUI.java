import javax.swing.*;
import java.awt.*;

public class LoginUI {
    private JFrame frame;
    private UserManager userManager;
    private JTextField usernameField;
    private JPasswordField passwordField;

    public LoginUI(UserManager userManager) {
        this.userManager = userManager;
        frame = new JFrame("登录");

        frame.setSize(300, 150);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new GridLayout(3, 2));

        frame.add(new JLabel("用户名:"));
        usernameField = new JTextField();
        frame.add(usernameField);

        frame.add(new JLabel("密码:"));
        passwordField = new JPasswordField();
        frame.add(passwordField);

        JButton loginButton = new JButton("登录");
        loginButton.addActionListener(e -> login());
        frame.add(loginButton);

        JButton registerButton = new JButton("注册");
        registerButton.addActionListener(e -> register());
        frame.add(registerButton);

        frame.setVisible(true);
    }

    private void login() {
        String username = usernameField.getText();
        String password = new String(passwordField.getPassword());
        if (userManager.login(username, password)) {
            JOptionPane.showMessageDialog(frame, "登录成功!");
            // 跳转到任务管理界面
            new TaskUI(new TaskManager(), username);  // 这里可以传递用户名来为每个用户存储任务
            frame.dispose();  // 关闭登录窗口
        } else {
            JOptionPane.showMessageDialog(frame, "用户名或密码错误!");
        }
    }

    private void register() {
        String username = usernameField.getText();
        String password = new String(passwordField.getPassword());
        if (userManager.register(username, password)) {
            JOptionPane.showMessageDialog(frame, "注册成功! 请登录.");
        } else {
            JOptionPane.showMessageDialog(frame, "用户名已存在!");
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new LoginUI(new UserManager()));
    }
}
