import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TaskManager {
    private Map<String, List<Task>> userTasks;  // 根据用户名存储任务
    private int taskIdCounter;

    public TaskManager() {
        this.userTasks = new HashMap<>();
        this.taskIdCounter = 1;
    }

    public void addTask(String username, String description) {
        Task newTask = new Task(taskIdCounter++, description);
        userTasks.putIfAbsent(username, new ArrayList<>());
        userTasks.get(username).add(newTask);
    }

    public void removeTask(String username, int taskId) {
        List<Task> tasks = userTasks.get(username);
        if (tasks != null) {
            tasks.removeIf(task -> task.getId() == taskId);
        }
    }

    public List<Task> getUserTasks(String username) {
        return userTasks.getOrDefault(username, new ArrayList<>());
    }

    public void markTaskAsCompleted(String username, int taskId) {
        List<Task> tasks = userTasks.get(username);
        if (tasks != null) {
            for (Task task : tasks) {
                if (task.getId() == taskId) {
                    task.markAsCompleted();
                    break;
                }
            }
        }
    }
}
