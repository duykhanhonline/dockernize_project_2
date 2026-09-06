import type { Task } from "../types";

interface TaskListProps {
  tasks: Task[];
  onToggle: (task: Task) => void;
  onDelete: (id: number) => void;
}

function TaskList({ tasks, onToggle, onDelete }: TaskListProps) {
  if (tasks.length === 0) {
    return <p>No tasks yet.</p>;
  }

  return (
    <ul className="task-list">
      {tasks.map((task) => (
        <li key={task.id} className={task.completed ? "completed" : ""}>
          <label>
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => onToggle(task)}
            />
            <span>{task.title}</span>
          </label>
          <button onClick={() => onDelete(task.id)} aria-label={`Delete ${task.title}`}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}

export default TaskList;
