'use client';

import React, { useState, useEffect } from 'react';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { Task } from '@/types';
import { ChatInterface } from '@/components/ChatInterface';
import { TaskList } from '@/components/TaskList';
import api from '@/lib/api';
import { cn } from '@/lib/utils';
import { AnimatePresence, motion } from 'framer-motion';

const USER_ID = process.env.NEXT_PUBLIC_DEMO_USER_ID || 'demo_user_123';

export default function ChatPage() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loadingTasks, setLoadingTasks] = useState(false);
    const [showTasks, setShowTasks] = useState(true);

    // Initial Fetch
    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            setLoadingTasks(true);
            const res = await api.get('/tasks', { params: { user_id: USER_ID, status: 'active' } }); // Only active? Or all? User might want to see completed. let's show all
            // Actually, for "Live Task List", usually focuses on Active. But Chat might complete one.
            // Let's fetch all and sort Active first.
            const allTasks = res.data as Task[];
            setTasks(allTasks.sort((a, b) => (a.status === 'active' ? -1 : 1)));
        } catch (err) {
            console.error(err);
        } finally {
            setLoadingTasks(false);
        }
    };

    const handleTaskUpdate = () => {
        console.log("Chat triggered task refresh!");
        fetchTasks();
    };

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden">

            {/* Main Chat Area - Takes full width on mobile, flexible on desktop */}
            <div className="flex-1 flex flex-col h-full bg-white relative z-10 shadow-xl">
                <div className="h-14 border-b border-gray-100 flex items-center px-4 justify-between bg-white shrink-0">
                    <Link href="/" className="flex items-center gap-2 text-gray-500 hover:text-blue-600 transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                        <span className="font-medium text-sm">Back to Dashboard</span>
                    </Link>
                    <button
                        onClick={() => setShowTasks(!showTasks)}
                        className="lg:hidden text-sm font-medium text-blue-600"
                    >
                        {showTasks ? "Hide Tasks" : "Show Tasks"}
                    </button>
                </div>
                <div className="flex-1 overflow-hidden relative">
                    <ChatInterface onTaskUpdate={handleTaskUpdate} />
                </div>
            </div>

            {/* Live Task List Sidebar - Hidden on mobile by default, sliding?? Or generic split pane */}
            {/* On Desktop: visible on right. On Mobile: Hidden or overlay? */}
            {/* The prompt said: "Two-pane layout" */}
            <AnimatePresence>
                {showTasks && (
                    <motion.div
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: "380px", opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        className="hidden lg:flex flex-col border-l border-gray-200 bg-gray-50 h-full shrink-0"
                    >
                        <div className="h-14 border-b border-gray-200 px-4 flex items-center justify-between bg-gray-50 shrink-0">
                            <h3 className="font-semibold text-gray-700">Live Tasks</h3>
                            <button onClick={fetchTasks} className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors rounded-md hover:bg-gray-100">
                                <RefreshCw className={cn("w-4 h-4", loadingTasks && "animate-spin")} />
                            </button>
                        </div>
                        <div className="flex-1 overflow-y-auto p-4">
                            <TaskList
                                tasks={tasks}
                                loading={loadingTasks}
                                viewMode="list" // Use list mode for sidebar
                                onEdit={() => { }} // Read only in chat sidebar for simplicity? Or open modal? (Modal state is complex to share)
                                onDelete={async (id) => {
                                    await api.delete(`/tasks/${id}`, { params: { user_id: USER_ID } });
                                    fetchTasks();
                                }}
                                onToggleStatus={async (task) => {
                                    const newStatus = task.status === 'completed' ? 'active' : 'completed';
                                    await api.put(`/tasks/${task.id}`, { ...task, status: newStatus }, { params: { user_id: USER_ID } });
                                    fetchTasks();
                                }}
                            />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

        </div>
    );
}
