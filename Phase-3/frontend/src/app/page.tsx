'use client';

import React, { useState, useEffect } from 'react';
import { Plus, CheckCircle, Circle, Trash2, Edit2, MessageSquare, Search, Filter, Loader2, X } from 'lucide-react';
import { Task } from '@/types';
import { ChatInterface } from '@/components/ChatInterface';
import { cn } from '@/lib/utils';
import api from '@/lib/api';
import { AnimatePresence, motion } from 'framer-motion';

const USER_ID = process.env.NEXT_PUBLIC_DEMO_USER_ID || 'demo_user_123';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'completed'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Chat Sidebar State
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [formData, setFormData] = useState({ title: '', description: '', priority: 'medium' });

  useEffect(() => {
    fetchTasks();
  }, [filterStatus]); // Refresh when filter changes? Or client side filter?

  // Let's do server-side filter for scalability, or client side for speed in demo?
  // I'll do server-side + search debounce could be added but simple is fine.

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params: any = { user_id: USER_ID };
      if (filterStatus !== 'all') params.status = filterStatus;
      if (searchQuery) params.search = searchQuery;

      const res = await api.get('/tasks', { params });
      setTasks(res.data);
    } catch (err) {
      console.error("Failed to fetch tasks", err);
    } finally {
      setLoading(false);
    }
  };

  // Debounced search effect
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchTasks();
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this task?')) return;
    try {
      await api.delete(`/tasks/${id}`, { params: { user_id: USER_ID } });
      setTasks(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleStatus = async (task: Task, e: React.MouseEvent) => {
    e.stopPropagation();
    const newStatus = task.status === 'completed' ? 'active' : 'completed';
    // Optimistic
    setTasks(prev => prev.map(t => t.id === task.id ? { ...t, status: newStatus } : t));

    try {
      await api.put(`/tasks/${task.id}`, { ...task, status: newStatus }, { params: { user_id: USER_ID } });
    } catch (err) {
      // Revert
      console.error(err);
      fetchTasks();
    }
  };

  const openModal = (task?: Task) => {
    if (task) {
      setEditingTask(task);
      setFormData({
        title: task.title,
        description: task.description || '',
        priority: task.priority
      });
    } else {
      setEditingTask(null);
      setFormData({ title: '', description: '', priority: 'medium' });
    }
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingTask) {
        const res = await api.put(`/tasks/${editingTask.id}`,
          { ...editingTask, ...formData },
          { params: { user_id: USER_ID } }
        );
        setTasks(prev => prev.map(t => t.id === editingTask.id ? res.data : t));
      } else {
        const res = await api.post('/tasks',
          { ...formData, status: 'active' },
          { params: { user_id: USER_ID } }
        );
        setTasks(prev => [res.data, ...prev]);
      }
      setIsModalOpen(false);
    } catch (err) {
      console.error(err);
    }
  };

  const getPriorityColor = (p: string) => {
    switch (p) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row overflow-hidden relative">

      {/* Main Content */}
      <div className={cn("flex-1 flex flex-col h-screen transition-all duration-300", isChatOpen ? "mr-0 md:mr-96" : "")}>

        {/* Header */}
        <header className="bg-white border-b border-gray-200 h-16 px-6 flex items-center justify-between sticky top-0 z-10 shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">T</div>
            <h1 className="text-xl font-bold text-gray-800">Todo App</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsChatOpen(!isChatOpen)}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg transition-all font-medium border",
                isChatOpen
                  ? "bg-blue-50 text-blue-600 border-blue-200"
                  : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50"
              )}
            >
              <MessageSquare className="w-4 h-4" />
              <span className="hidden sm:inline">AI Assistant</span>
            </button>
            <button
              onClick={() => openModal()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition-colors shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">New Task</span>
            </button>
          </div>
        </header>

        {/* Toolbar */}
        <div className="px-6 py-4 flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="relative w-full sm:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            />
          </div>
          <div className="flex gap-2 bg-white p-1 rounded-lg border border-gray-200">
            {(['all', 'active', 'completed'] as const).map(status => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={cn(
                  "px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-all",
                  filterStatus === status ? "bg-blue-100 text-blue-700 shadow-sm" : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                )}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        {/* Task Grid */}
        <div className="flex-1 overflow-y-auto px-6 pb-20">
          {loading ? (
            <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-gray-400" /></div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-20 text-gray-400">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-gray-300" />
              </div>
              <p className="text-lg font-medium text-gray-500">No tasks found</p>
              <p className="text-sm">Create a new task or ask the AI to help!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <AnimatePresence>
                {tasks.map(task => (
                  <motion.div
                    key={task.id}
                    layout
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className={cn(
                      "bg-white p-4 rounded-xl border transition-all hover:shadow-md group",
                      task.status === 'completed' ? "border-green-100 bg-green-50/30" : "border-gray-200"
                    )}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={cn("text-xs px-2 py-0.5 rounded-full border font-medium capitalize", getPriorityColor(task.priority))}>
                        {task.priority}
                      </span>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => openModal(task)} className="p-1 text-gray-400 hover:text-blue-600 rounded hover:bg-blue-50"><Edit2 className="w-4 h-4" /></button>
                        <button onClick={(e) => handleDelete(task.id, e)} className="p-1 text-gray-400 hover:text-red-600 rounded hover:bg-red-50"><Trash2 className="w-4 h-4" /></button>
                      </div>
                    </div>

                    <h3 className={cn("font-semibold text-gray-800 mb-1 line-clamp-1", task.status === 'completed' && "line-through text-gray-400")}>{task.title}</h3>
                    <p className={cn("text-sm text-gray-500 mb-4 line-clamp-2 min-h-[40px]", task.status === 'completed' && "line-through text-gray-300")}>{task.description || "No description"}</p>

                    <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                      <span className="text-xs text-gray-400">{new Date(task.updated_at).toLocaleDateString()}</span>
                      <button
                        onClick={(e) => handleToggleStatus(task, e)}
                        className={cn(
                          "flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors",
                          task.status === 'completed'
                            ? "bg-green-100 text-green-700 hover:bg-green-200"
                            : "bg-gray-100 text-gray-600 hover:bg-gray-200 group-hover:bg-blue-50 group-hover:text-blue-600"
                        )}
                      >
                        {task.status === 'completed' ? (
                          <><CheckCircle className="w-3.5 h-3.5" /> Completed</>
                        ) : (
                          <><Circle className="w-3.5 h-3.5" /> Mark Done</>
                        )}
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>

      {/* Chat Sidebar / Overlay */}
      <AnimatePresence>
        {isChatOpen && (
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed inset-y-0 right-0 z-40 w-full md:w-96 shadow-2xl border-l border-gray-200 bg-white"
          >
            <ChatInterface onClose={() => setIsChatOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Task Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
              <h2 className="text-lg font-bold text-gray-800">{editingTask ? 'Edit Task' : 'New Task'}</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  autoFocus
                  type="text"
                  value={formData.title}
                  onChange={e => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all h-24 resize-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <div className="flex gap-2">
                  {(['low', 'medium', 'high']).map(p => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setFormData({ ...formData, priority: p })}
                      className={cn(
                        "flex-1 py-2 text-sm font-medium rounded-lg border capitalize transition-all",
                        formData.priority === p
                          ? getPriorityColor(p) + " ring-2 ring-offset-1 ring-blue-500/30 shadow-sm"
                          : "border-gray-200 text-gray-600 hover:bg-gray-50"
                      )}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
              <div className="pt-4 flex gap-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="flex-1 py-2.5 text-gray-600 font-medium hover:bg-gray-50 rounded-lg">Cancel</button>
                <button type="submit" className="flex-1 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 shadow-sm">Save Task</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
