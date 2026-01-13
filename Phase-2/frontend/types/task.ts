export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'active' | 'completed';
  priority: 'low' | 'medium' | 'high';
  due_date?: string; // ISO string
  completed_at?: string | null; // ISO string
  created_at: string; // ISO string
  updated_at: string; // ISO string
  user_id: string;
}

export interface TaskCreateData {
  title: string;
  description?: string;
  status?: 'active' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  due_date?: string; // ISO string
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
  status?: 'active' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  due_date?: string; // ISO string
}