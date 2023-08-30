import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        TaskManager manager = new TaskManager();
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("请选择一个选项：");
            System.out.println("1. 增加任务");
            System.out.println("2. 删除任务");
            System.out.println("3. 查看所有任务");
            System.out.println("4. 标记任务为已完成");
            System.out.println("5. 退出");

            int choice = scanner.nextInt();
            scanner.nextLine();

            switch (choice) {
                case 1:
                    System.out.println("请输入任务描述：");
                    String description = scanner.nextLine();
                    manager.addTask(description);
                    break;
                case 2:
                    System.out.println("请输入要删除的任务ID：");
                    int idToDelete = scanner.nextInt();
                    manager.removeTask(idToDelete);
                    break;
                case 3:
                    for (Task task : manager.getAllTasks()) {
                        System.out.println(task);
                    }
                    break;
                case 4:
                    System.out.println("请输入要标记为已完成的任务ID：");
                    int idToComplete = scanner.nextInt();
                    manager.markTaskAsCompleted(idToComplete);
                    break;
                case 5:
                    System.out.println("再见！");
                    scanner.close();
                    return;
                default:
                    System.out.println("无效选项，请重新选择。");
            }
        }
    }
}
