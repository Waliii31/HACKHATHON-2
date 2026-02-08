import { Task, TaskCreateData, TaskUpdateData } from '@/types/task';
import { useState } from 'react';

interface TaskFormProps {
  initialData?: Task;
  onSubmit: (data: TaskCreateData | TaskUpdateData) => void | Promise<void>;
  onCancel: () => void;
  submitLabel: string;
}

export const TaskForm = ({ initialData, onSubmit, onCancel, submitLabel }: TaskFormProps) => {
  const isEditing = !!initialData;

  const [formData, setFormData] = useState<TaskCreateData>({
    title: initialData?.title || '',
    description: initialData?.description || '',
    status: initialData?.status || 'active',
    priority: initialData?.priority || 'medium',
    due_date: initialData?.due_date || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length > 255) {
      newErrors.title = 'Title must be 255 characters or less';
    }

    if (formData.description && formData.description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label htmlFor="title" className="block text-xs font-medium uppercase tracking-wide text-slate-400">
          Title *
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={`mt-2 w-full rounded-xl border px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 ${
            errors.title
              ? 'border-red-400/60 bg-red-500/10 focus:border-red-400 focus:ring-red-500/30'
              : 'border-white/10 bg-slate-900/60 focus:border-blue-400 focus:ring-blue-500/30'
          }`}
          placeholder="Design the onboarding flow"
        />
        {errors.title && <p className="mt-1 text-sm text-red-300">{errors.title}</p>}
      </div>

      <div>
        <label htmlFor="description" className="block text-xs font-medium uppercase tracking-wide text-slate-400">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className={`mt-2 w-full rounded-xl border px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 ${
            errors.description
              ? 'border-red-400/60 bg-red-500/10 focus:border-red-400 focus:ring-red-500/30'
              : 'border-white/10 bg-slate-900/60 focus:border-blue-400 focus:ring-blue-500/30'
          }`}
          placeholder="Add a short summary to keep context."
        />
        {errors.description && <p className="mt-1 text-sm text-red-300">{errors.description}</p>}
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div>
          <label htmlFor="priority" className="block text-xs font-medium uppercase tracking-wide text-slate-400">
            Priority
          </label>
          <select
            id="priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900/60 px-3 py-2 text-sm text-white focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="status" className="block text-xs font-medium uppercase tracking-wide text-slate-400">
            Status
          </label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900/60 px-3 py-2 text-sm text-white focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          >
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        <div>
          <label htmlFor="due_date" className="block text-xs font-medium uppercase tracking-wide text-slate-400">
            Due date
          </label>
          <input
            type="date"
            id="due_date"
            name="due_date"
            value={formData.due_date}
            onChange={handleChange}
            className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900/60 px-3 py-2 text-sm text-white focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          className="rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition hover:from-blue-400 hover:to-indigo-500"
        >
          {submitLabel}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-xl border border-white/10 bg-white/5 px-5 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/10"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};
