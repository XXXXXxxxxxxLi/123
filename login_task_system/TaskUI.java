import javax.swing.*;
import java.awt.*;

public class TaskUI {
    private JFrame frame;
    private TaskManager manager;
    private String username;
    private DefaultListModel<String> listModel;
    private JList<String> taskList;

    public TaskUI(TaskManager manager, String username) {
        this.manager = manager;
        this.username = username;
        frame = new JFrame("任务管理器 - " + username);

        frame.setSize(400, 400);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        listModel = new DefaultListModel<>();
        taskList = new JList<>(listModel);
        frame.add(new JScrollPane(taskList), BorderLayout.CENTER);

        JPanel panel = new JPanel();
        JTextField taskInput = new JTextField(15);
        JButton addButton = new JButton("增加任务");
        addButton.addActionListener(e -> {
            manager.addTask(username, taskInput.getText());
            refreshList();
            taskInput.setText("");
        });

        JButton removeButton = new JButton("删除任务");
        removeButton.addActionListener(e -> {
            if (taskList.getSelectedIndex() != -1) {
                manager.removeTask(username, taskList.getSelectedIndex() + 1);  // ID starts from 1
                refreshList();
            }
        });

        JButton markAsDoneButton = new JButton("标记为已完成");
        markAsDoneButton.addActionListener(e -> {
            if (taskList.getSelectedIndex() != -1) {
                manager.markTaskAsCompleted(username, taskList.getSelectedIndex() + 1);  // ID starts from 1
                refreshList();
            }
        });

        panel.add(taskInput);
        panel.add(addButton);
        panel.add(removeButton);
        panel.add(markAsDoneButton);

        frame.add(panel, BorderLayout.SOUTH);

        refreshList();

        frame.setVisible(true);
    }

    private void refreshList() {
        listModel.clear();
        for (Task task : manager.getUserTasks(username)) {
            listModel.addElement(task.toString());
        }
    }
}
