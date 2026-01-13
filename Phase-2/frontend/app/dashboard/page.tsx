'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { Task } from '@/types/task';
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

  const handleCreateTask = async (taskData: Omit<Task, 'id' | 'user_id' | 'created_at' | 'updated_at'>) => {
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
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">My Tasks</h1>
        <p className="text-gray-600">Welcome back, {user?.name}!</p>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Left sidebar */}
        <div className="w-full md:w-64 flex-shrink-0">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Actions</h2>
            <button
              onClick={() => {
                setEditingTask(null);
                setShowForm(!showForm);
              }}
              className={`w-full mb-3 py-2 px-4 rounded-md ${
                showForm
                  ? 'bg-gray-200 text-gray-800'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {showForm ? 'Cancel' : 'Add New Task'}
            </button>

            <div className="mt-6">
              <h3 className="font-medium mb-2">Filter</h3>
              <div className="space-y-2">
                {(['all', 'active', 'completed'] as const).map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`w-full text-left py-1 px-3 rounded ${
                      filter === f
                        ? 'bg-blue-100 text-blue-700'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    {f.charAt(0).toUpperCase() + f.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t">
              <h3 className="font-medium mb-2">Stats</h3>
              <div className="text-sm text-gray-600">
                <p>Total: {tasks.length}</p>
                <p>Active: {tasks.filter(t => t.status === 'active').length}</p>
                <p>Completed: {tasks.filter(t => t.status === 'completed').length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1">
          {showForm && (
            <div className="mb-6">
              <TaskForm
                onSubmit={handleCreateTask}
                onCancel={() => setShowForm(false)}
                submitLabel="Create Task"
              />
            </div>
          )}

          {editingTask && (
            <div className="mb-6">
              <TaskForm
                initialData={editingTask}
                onSubmit={(data) => handleUpdateTask(editingTask.id, data)}
                onCancel={() => setEditingTask(null)}
                submitLabel="Update Task"
              />
            </div>
          )}

          {filteredTasks.length === 0 ? (
            <div className="bg-white p-8 rounded-lg shadow text-center">
              <p className="text-gray-500">No tasks found. {filter === 'all' ? 'Create your first task!' : `Try changing the filter.`}</p>
            </div>
          ) : (
            <div className="space-y-4">
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