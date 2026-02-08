import { Task } from '@/types/task';
import { Trash2, Edit3, CheckCircle, Circle } from 'lucide-react';
import { useState } from 'react';

interface TaskItemProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onToggleComplete: (taskId: string, complete: boolean) => void;
}

export const TaskItem = ({ task, onEdit, onDelete, onToggleComplete }: TaskItemProps) => {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const getPriorityClass = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-rose-500/20 text-rose-200';
      case 'medium':
        return 'bg-amber-500/20 text-amber-200';
      case 'low':
        return 'bg-emerald-500/20 text-emerald-200';
      default:
        return 'bg-slate-500/20 text-slate-200';
    }
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-lg shadow-black/20">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <button
            onClick={() => onToggleComplete(task.id, task.status === 'active')}
            className="mt-1 rounded-full border border-white/10 bg-white/5 p-2 text-slate-200 transition hover:bg-white/10 focus:outline-none"
            aria-label={task.status === 'active' ? 'Mark as complete' : 'Mark as active'}
          >
            {task.status === 'active' ? (
              <Circle className="h-5 w-5 text-slate-300" />
            ) : (
              <CheckCircle className="h-5 w-5 text-emerald-400" />
            )}
          </button>

          <div className="flex-1">
            <h3
              className={`text-lg font-semibold ${
                task.status === 'completed' ? 'line-through text-slate-500' : 'text-white'
              }`}
            >
              {task.title}
            </h3>

            {task.description && (
              <p className={`mt-1 text-sm text-slate-300 ${task.status === 'completed' ? 'line-through' : ''}`}>
                {task.description}
              </p>
            )}

            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className={`rounded-full px-2.5 py-1 font-medium ${getPriorityClass(task.priority)}`}>
                {task.priority}
              </span>

              {task.due_date && (
                <span className="rounded-full bg-blue-500/20 px-2.5 py-1 font-medium text-blue-200">
                  Due: {formatDate(task.due_date)}
                </span>
              )}

              {task.status === 'completed' && task.completed_at && (
                <span className="rounded-full bg-emerald-500/20 px-2.5 py-1 font-medium text-emerald-200">
                  Completed: {formatDate(task.completed_at)}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onEdit(task)}
            className="rounded-full border border-white/10 bg-white/5 p-2 text-slate-200 transition hover:bg-white/10 hover:text-white focus:outline-none"
            aria-label="Edit task"
          >
            <Edit3 className="h-4 w-4" />
          </button>

          {showConfirmDelete ? (
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  onDelete(task.id);
                  setShowConfirmDelete(false);
                }}
                className="rounded-full border border-red-500/40 bg-red-500/10 p-2 text-red-200 transition hover:bg-red-500/20 focus:outline-none"
                aria-label="Confirm delete"
              >
                <Trash2 className="h-4 w-4" />
              </button>
              <button
                onClick={() => setShowConfirmDelete(false)}
                className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-slate-200 transition hover:bg-white/10 focus:outline-none"
                aria-label="Cancel delete"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowConfirmDelete(true)}
              className="rounded-full border border-white/10 bg-white/5 p-2 text-slate-200 transition hover:bg-white/10 hover:text-red-200 focus:outline-none"
              aria-label="Delete task"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
