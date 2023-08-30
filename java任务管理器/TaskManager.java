import java.util.ArrayList;
import java.util.List;

public class TaskManager {
    private List<Task> tasks;
    private int taskIdCounter;

    public TaskManager() {
        this.tasks = new ArrayList<>();
        this.taskIdCounter = 1;
    }

    public void addTask(String description) {
        Task newTask = new Task(taskIdCounter++, description);
        tasks.add(newTask);
    }

    public void removeTask(int taskId) {
        tasks.removeIf(task -> task.getId() == taskId);
    }

    public List<Task> getAllTasks() {
        return tasks;
    }

    public void markTaskAsCompleted(int taskId) {
        for (Task task : tasks) {
            if (task.getId() == taskId) {
                task.markAsCompleted();
                break;
            }
        }
    }
}
