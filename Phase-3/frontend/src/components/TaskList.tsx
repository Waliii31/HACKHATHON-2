'use client';

import React from 'react';
import { CheckCircle, Circle, Trash2, Edit2 } from 'lucide-react';
import { Task } from '@/types';
import { cn } from '@/lib/utils';
import { AnimatePresence, motion } from 'framer-motion';

interface TaskListProps {
    tasks: Task[];
    loading?: boolean;
    onEdit: (task: Task) => void;
    onDelete: (id: string) => void;
    onToggleStatus: (task: Task) => void;
    viewMode?: 'grid' | 'list';
}

export function TaskList({ tasks, loading, onEdit, onDelete, onToggleStatus, viewMode = 'grid' }: TaskListProps) {

    const getPriorityColor = (p: string) => {
        switch (p) {
            case 'high': return 'bg-red-100 text-red-700 border-red-200';
            case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
            case 'low': return 'bg-green-100 text-green-700 border-green-200';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center p-8">
                <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            </div>
        );
    }

    if (tasks.length === 0) {
        return (
            <div className="text-center py-10 text-gray-400">
                <p>No tasks found</p>
            </div>
        );
    }

    return (
        <div className={cn(
            "gap-4",
            viewMode === 'grid' ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3" : "flex flex-col space-y-3"
        )}>
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
                                <button onClick={() => onEdit(task)} className="p-1 text-gray-400 hover:text-blue-600 rounded hover:bg-blue-50"><Edit2 className="w-4 h-4" /></button>
                                <button onClick={() => onDelete(task.id)} className="p-1 text-gray-400 hover:text-red-600 rounded hover:bg-red-50"><Trash2 className="w-4 h-4" /></button>
                            </div>
                        </div>

                        <h3 className={cn("font-semibold text-gray-800 mb-1 line-clamp-1", task.status === 'completed' && "line-through text-gray-400")}>{task.title}</h3>
                        {viewMode === 'grid' && (
                            <p className={cn("text-sm text-gray-500 mb-4 line-clamp-2 min-h-[40px]", task.status === 'completed' && "line-through text-gray-300")}>{task.description || "No description"}</p>
                        )}

                        <div className="flex items-center justify-between pt-2 border-t border-gray-100 mt-auto">
                            <span className="text-xs text-gray-400">{new Date(task.updated_at).toLocaleDateString()}</span>
                            <button
                                onClick={() => onToggleStatus(task)}
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
    );
}
