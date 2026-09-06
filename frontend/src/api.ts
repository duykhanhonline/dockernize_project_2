import type { Task } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export function getTasks(): Promise<Task[]> {
  return fetch(`${API_BASE_URL}/api/tasks`).then((res) => handleResponse<Task[]>(res));
}

export function createTask(title: string): Promise<Task> {
  return fetch(`${API_BASE_URL}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  }).then((res) => handleResponse<Task>(res));
}

export function updateTask(id: number, changes: Partial<Pick<Task, "title" | "completed">>): Promise<Task> {
  return fetch(`${API_BASE_URL}/api/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(changes),
  }).then((res) => handleResponse<Task>(res));
}

export function deleteTask(id: number): Promise<void> {
  return fetch(`${API_BASE_URL}/api/tasks/${id}`, {
    method: "DELETE",
  }).then((res) => handleResponse<void>(res));
}
