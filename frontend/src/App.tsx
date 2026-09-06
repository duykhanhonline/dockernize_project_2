import { useEffect, useState } from "react";
import "./App.css";
import TaskForm from "./components/TaskForm";
import TaskList from "./components/TaskList";
import { createTask, deleteTask, getTasks, updateTask } from "./api";
import type { Task } from "./types";

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    setLoading(true);
    setError(null);
    try {
      const data = await getTasks();
      setTasks(data);
    } catch {
      setError("Failed to load tasks. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd(title: string) {
    setError(null);
    try {
      const task = await createTask(title);
      setTasks((prev) => [...prev, task]);
    } catch {
      setError("Failed to add task.");
    }
  }

  async function handleToggle(task: Task) {
    setError(null);
    try {
      const updated = await updateTask(task.id, { completed: !task.completed });
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch {
      setError("Failed to update task.");
    }
  }

  async function handleDelete(id: number) {
    setError(null);
    try {
      await deleteTask(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch {
      setError("Failed to delete task.");
    }
  }

  return (
    <main className="app">
      <h1>Task Board</h1>
      <TaskForm onAdd={handleAdd} />
      {error && <p className="error">{error}</p>}
      {loading ? <p>Loading tasks...</p> : (
        <TaskList tasks={tasks} onToggle={handleToggle} onDelete={handleDelete} />
      )}
    </main>
  );
}

export default App;
