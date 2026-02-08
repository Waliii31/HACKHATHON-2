'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { Task, TaskCreateData } from '@/types/task';
import { TaskForm } from '@/components/task-form';
import { TaskItem } from '@/components/task-item';
import { TaskApi } from '@/lib/api-client';
import { AuthGuard } from '@/components/auth-guard';

const DashboardContent = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const { user, isLoading: authLoading, getToken } = useAuth();

  useEffect(() => {
    if (user) {
      fetchTasks();
    }
  }, [user]);

  const fetchTasks = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const token = await getToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
      const fetchedTasks = await TaskApi.getTasks(user.id, token);
      setTasks(fetchedTasks);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (taskData: TaskCreateData) => {
    if (!user) return;

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
      const newTask = await TaskApi.createTask(user.id, taskData, token);
      setTasks([newTask, ...tasks]);
      setShowForm(false);
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleUpdateTask = async (taskId: string, taskData: Partial<Task>) => {
    if (!user) return;

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
      const updatedTask = await TaskApi.updateTask(user.id, taskId, taskData, token);
      setTasks(tasks.map(t => t.id === taskId ? updatedTask : t));
      setEditingTask(null);
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!user) return;

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
      await TaskApi.deleteTask(user.id, taskId, token);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const handleToggleComplete = async (taskId: string, complete: boolean) => {
    if (!user) return;

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
      const updatedTask = await TaskApi.toggleTaskCompletion(user.id, taskId, complete, token);
      setTasks(tasks.map(t => t.id === taskId ? updatedTask : t));
    } catch (error) {
      console.error('Failed to toggle task completion:', error);
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return task.status === 'active';
    if (filter === 'completed') return task.status === 'completed';
    return true;
  });

  if (authLoading || loading) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <p className="text-sm text-slate-300">Loading your workspace...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <header className="flex flex-col gap-6 rounded-3xl border border-white/10 bg-gradient-to-br from-white/5 via-white/10 to-white/5 p-8 shadow-2xl shadow-blue-500/10">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-blue-300">Workspace</p>
            <h1 className="mt-2 text-3xl font-semibold text-white md:text-4xl">Welcome back, {user?.name}.</h1>
            <p className="mt-2 text-sm text-slate-300">Plan, prioritize, and complete tasks with focus.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => {
                setEditingTask(null);
                setShowForm(!showForm);
              }}
              className={`inline-flex items-center gap-2 rounded-full px-5 py-2 text-sm font-semibold transition ${
                showForm
                  ? 'border border-white/10 bg-white/10 text-slate-200 hover:bg-white/20'
                  : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30 hover:from-blue-400 hover:to-indigo-500'
              }`}
            >
              {showForm ? 'Close form' : 'New task'}
            </button>
            <a
              href="http://localhost:3002"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-5 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/10"
            >
              <span className="text-lg">🤖</span>
              AI Assistant
            </a>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {[
            { label: 'Total tasks', value: tasks.length },
            { label: 'Active', value: tasks.filter(t => t.status === 'active').length },
            { label: 'Completed', value: tasks.filter(t => t.status === 'completed').length },
          ].map((stat) => (
            <div key={stat.label} className="rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{stat.label}</p>
              <p className="mt-2 text-2xl font-semibold text-white">{stat.value}</p>
            </div>
          ))}
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
        <aside className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <h2 className="text-sm font-semibold text-white">Filters</h2>
            <div className="mt-4 space-y-2">
              {(['all', 'active', 'completed'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`w-full rounded-xl px-3 py-2 text-left text-sm font-medium transition ${
                    filter === f
                      ? 'bg-white/15 text-white'
                      : 'text-slate-300 hover:bg-white/10'
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-blue-500/20 to-indigo-500/20 p-4 text-sm text-slate-200">
            <p className="font-semibold text-white">Focus tip</p>
            <p className="mt-2">Keep three high-priority tasks for a calmer day.</p>
          </div>
        </aside>

        <section className="space-y-6">
          {showForm && (
            <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-2xl shadow-blue-500/10">
              <h3 className="text-lg font-semibold text-white">Create a new task</h3>
              <p className="mt-1 text-sm text-slate-400">Capture what needs your attention today.</p>
              <div className="mt-4">
                <TaskForm
                  onSubmit={(data) => handleCreateTask(data as TaskCreateData)}
                  onCancel={() => setShowForm(false)}
                  submitLabel="Create Task"
                />
              </div>
            </div>
          )}

          {editingTask && (
            <div className="rounded-3xl border border-blue-500/20 bg-slate-950/70 p-6 shadow-2xl shadow-blue-500/10">
              <h3 className="text-lg font-semibold text-white">Edit task</h3>
              <p className="mt-1 text-sm text-slate-400">Refine the details and keep going.</p>
              <div className="mt-4">
                <TaskForm
                  initialData={editingTask}
                  onSubmit={(data) => handleUpdateTask(editingTask.id, data)}
                  onCancel={() => setEditingTask(null)}
                  submitLabel="Save Changes"
                />
              </div>
            </div>
          )}

          {filteredTasks.length === 0 ? (
            <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center text-slate-200">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white/10 text-2xl">
                ✨
              </div>
              <h3 className="mt-4 text-lg font-semibold text-white">No tasks here yet</h3>
              <p className="mt-2 text-sm text-slate-400">
                {filter === 'all'
                  ? 'Start by adding your first task to build momentum.'
                  : `Nothing marked as ${filter}. Try a different filter.`}
              </p>
              {filter === 'all' && (
                <button
                  onClick={() => setShowForm(true)}
                  className="mt-6 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-500/30"
                >
                  + Create first task
                </button>
              )}
            </div>
          ) : (
            <div className="grid gap-4">
              {filteredTasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onEdit={() => {
                    setEditingTask(task);
                    setShowForm(false);
                  }}
                  onDelete={handleDeleteTask}
                  onToggleComplete={handleToggleComplete}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  );
}
