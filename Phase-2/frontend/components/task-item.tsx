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
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
      <div className="flex justify-between items-start">
        <div className="flex items-start space-x-3">
          <button
            onClick={() => onToggleComplete(task.id, task.status === 'active')}
            className="mt-1 focus:outline-none"
            aria-label={task.status === 'active' ? 'Mark as complete' : 'Mark as active'}
          >
            {task.status === 'active' ? (
              <Circle className="h-5 w-5 text-gray-400 hover:text-blue-500" />
            ) : (
              <CheckCircle className="h-5 w-5 text-green-500" />
            )}
          </button>

          <div className="flex-1">
            <h3 className={`text-lg font-medium ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-800'}`}>
              {task.title}
            </h3>

            {task.description && (
              <p className={`mt-1 text-gray-600 ${task.status === 'completed' ? 'line-through' : ''}`}>
                {task.description}
              </p>
            )}

            <div className="mt-2 flex flex-wrap gap-2">
              <span className={`px-2 py-1 text-xs rounded-full ${getPriorityClass(task.priority)}`}>
                {task.priority}
              </span>

              {task.due_date && (
                <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                  Due: {formatDate(task.due_date)}
                </span>
              )}

              {task.status === 'completed' && task.completed_at && (
                <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                  Completed: {formatDate(task.completed_at)}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(task)}
            className="p-2 text-gray-500 hover:text-blue-600 focus:outline-none"
            aria-label="Edit task"
          >
            <Edit3 className="h-4 w-4" />
          </button>

          {showConfirmDelete ? (
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  onDelete(task.id);
                  setShowConfirmDelete(false);
                }}
                className="p-2 text-red-600 hover:text-red-800 focus:outline-none"
                aria-label="Confirm delete"
              >
                <Trash2 className="h-4 w-4" />
              </button>
              <button
                onClick={() => setShowConfirmDelete(false)}
                className="p-2 text-gray-500 hover:text-gray-700 focus:outline-none"
                aria-label="Cancel delete"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowConfirmDelete(true)}
              className="p-2 text-gray-500 hover:text-red-600 focus:outline-none"
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