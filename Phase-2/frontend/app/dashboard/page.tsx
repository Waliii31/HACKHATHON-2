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
      // Get the token from Better Auth session
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
      // Get the token from Better Auth session
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
      // Get the token from Better Auth session
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
      // Get the token from Better Auth session
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
      // Get the token from Better Auth session
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
      <div className="flex justify-center items-center min-h-[80vh]">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-2">My Tasks</h1>
            <p className="text-gray-500 font-medium">Welcome back, {user?.name}!</p>
          </div>
          <a
            href="http://localhost:3002"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 rounded-xl hover:shadow-lg hover:scale-105 transition-all duration-200 font-medium shadow-md"
          >
            <span className="text-xl">🤖</span>
            Chat with AI Assistant
          </a>
        </header>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Left sidebar */}
          <aside className="w-full lg:w-72 flex-shrink-0 space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100/50 backdrop-blur-xl">
              <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span>⚡</span>
                Quick Actions
              </h2>
              <button
                onClick={() => {
                  setEditingTask(null);
                  setShowForm(!showForm);
                }}
                className={`w-full py-3 px-4 rounded-xl font-medium transition-all duration-200 shadow-sm ${showForm
                    ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-blue-200'
                  }`}
              >
                {showForm ? 'Cancel Creation' : 'Create New Task'}
              </button>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100/50">
              <h3 className="font-bold text-gray-800 mb-4">Filters</h3>
              <div className="space-y-2">
                {(['all', 'active', 'completed'] as const).map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`w-full text-left py-2.5 px-4 rounded-xl transition-colors font-medium ${filter === f
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-50'
                      }`}
                  >
                    {f.charAt(0).toUpperCase() + f.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl border border-blue-100">
              <h3 className="font-bold text-blue-900 mb-4">Overview</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-blue-700/70">Total Tasks</span>
                  <span className="font-bold text-blue-900 bg-white px-2 py-1 rounded-lg">{tasks.length}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-blue-700/70">Active</span>
                  <span className="font-bold text-blue-900 bg-white px-2 py-1 rounded-lg">{tasks.filter(t => t.status === 'active').length}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-blue-700/70">Completed</span>
                  <span className="font-bold text-blue-900 bg-white px-2 py-1 rounded-lg">{tasks.filter(t => t.status === 'completed').length}</span>
                </div>
              </div>
            </div>
          </aside>

          {/* Main content */}
          <main className="flex-1 min-w-0">
            {showForm && (
              <div className="mb-8 bg-white p-6 rounded-2xl shadow-lg border border-gray-100 animate-in fade-in slide-in-from-top-4 duration-300">
                <h3 className="text-lg font-bold mb-4">Create New Task</h3>
                <TaskForm
                  onSubmit={(data) => handleCreateTask(data as TaskCreateData)}
                  onCancel={() => setShowForm(false)}
                  submitLabel="Create Task"
                />
              </div>
            )}

            {editingTask && (
              <div className="mb-8 bg-white p-6 rounded-2xl shadow-lg border border-blue-100 ring-2 ring-blue-50 animate-in fade-in slide-in-from-top-4 duration-300">
                <h3 className="text-lg font-bold mb-4 text-blue-700">Edit Task</h3>
                <TaskForm
                  initialData={editingTask}
                  onSubmit={(data) => handleUpdateTask(editingTask.id, data)}
                  onCancel={() => setEditingTask(null)}
                  submitLabel="Save Changes"
                />
              </div>
            )}

            {filteredTasks.length === 0 ? (
              <div className="bg-white p-12 rounded-3xl shadow-sm border border-gray-100 text-center">
                <div className="bg-gray-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl">📝</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">No tasks found</h3>
                <p className="text-gray-500 mb-8">
                  {filter === 'all'
                    ? "You haven't created any tasks yet. Get started and stay organized!"
                    : `No ${filter} tasks found. Try changing your filter.`}
                </p>
                {filter === 'all' && (
                  <button
                    onClick={() => setShowForm(true)}
                    className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors font-medium"
                  >
                    <span>+</span> Create First Task
                  </button>
                )}
              </div>
            ) : (
              <div className="grid gap-4">
                {filteredTasks.map((task) => (
                  <div key={task.id} className="transition-all duration-200 hover:translate-y-[-2px]">
                    <TaskItem
                      task={task}
                      onEdit={() => {
                        setEditingTask(task);
                        setShowForm(false);
                      }}
                      onDelete={handleDeleteTask}
                      onToggleComplete={handleToggleComplete}
                    />
                  </div>
                ))}
              </div>
            )}
          </main>
        </div>
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