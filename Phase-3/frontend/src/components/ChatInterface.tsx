'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Menu, Plus, Trash2, X, MessageSquare, Loader2 } from 'lucide-react';
import { Message, ChatResponse, Conversation } from '@/types';
import { MessageBubble } from '@/components/MessageBubble';
import { cn } from '@/lib/utils';
import api from '@/lib/api';
import { AnimatePresence, motion } from 'framer-motion';

const USER_ID = process.env.NEXT_PUBLIC_DEMO_USER_ID || 'demo_user_123';

export function ChatInterface({ onClose, onTaskUpdate }: { onClose?: () => void; onTaskUpdate?: () => void }) {
    // State
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);

    // Sidebar State
    const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Mobile
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loadingConversations, setLoadingConversations] = useState(false);

    // Refs
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Fetch conversations on load
    useEffect(() => {
        fetchConversations();
    }, []);

    const fetchConversations = async () => {
        try {
            setLoadingConversations(true);
            const res = await api.get('/chat/conversations', { params: { limit: 50, user_id: USER_ID } });
            setConversations(res.data.conversations || []);
        } catch (err) {
            console.error('Failed to fetch conversations', err);
        } finally {
            setLoadingConversations(false);
        }
    };

    const loadConversation = async (id: string) => {
        try {
            setIsLoading(true);
            const res = await api.get(`/chat/conversations/${id}`, { params: { user_id: USER_ID } });

            // Map backend messages to frontend format
            const mappedMessages: Message[] = res.data.messages.map((m: any) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                tools_used: m.tools_used,
                timestamp: m.created_at
            }));

            setMessages(mappedMessages);
            setConversationId(res.data.id);
            setIsSidebarOpen(false); // Close mobile sidebar
        } catch (err) {
            console.error('Failed to load conversation', err);
        } finally {
            setIsLoading(false);
        }
    };

    const deleteConversation = async (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this conversation?')) return;

        try {
            await api.delete(`/chat/conversations/${id}`, { params: { user_id: USER_ID } });
            setConversations(prev => prev.filter(c => c.id !== id));
            if (conversationId === id) {
                setConversationId(null);
                setMessages([]);
            }
        } catch (err) {
            console.error('Failed to delete', err);
        }
    };

    const startNewChat = () => {
        setConversationId(null);
        setMessages([]);
        setIsSidebarOpen(false);
    };

    const sendMessage = async () => {
        if (!inputValue.trim() || isLoading) return;

        const userMsgContent = inputValue.trim();
        setInputValue('');

        // Optimistic UI update
        const tempId = Date.now().toString();
        const optimisticMsg: Message = {
            id: tempId,
            role: 'user',
            content: userMsgContent,
            timestamp: new Date().toISOString(),
            isOptimistic: true
        };

        setMessages(prev => [...prev, optimisticMsg]);
        setIsLoading(true);

        try {
            const payload = {
                user_id: USER_ID,
                message: userMsgContent,
                conversation_id: conversationId // Optional
            };

            const res = await api.post('/chat', payload);
            const data: ChatResponse = res.data;

            // Update conversation ID if it was new
            if (!conversationId) {
                setConversationId(data.conversation_id);
                fetchConversations(); // Refresh list to show new chat
            }

            // Add AI Response
            const aiMsg: Message = {
                id: data.message_id,
                role: 'assistant',
                content: data.response,
                tools_used: data.tools_used,
                timestamp: data.timestamp
            };

            setMessages(prev => [...prev, aiMsg]);

            // Check for task updates
            if (onTaskUpdate && data.tools_used && data.tools_used.some(t => t.success)) {
                setTimeout(() => onTaskUpdate(), 500);
            }

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: "⚠️ Sorry, I encountered an error executing your request.",
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex h-full bg-[var(--bg-primary)] text-white font-sans overflow-hidden pattern-dots-sm text-gray-400">

            {/* Mobile Sidebar Overlay */}
            {isSidebarOpen && (
                <div
                    className="absolute inset-0 bg-black/60 z-20 lg:hidden backdrop-blur-md"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={cn(
                "absolute inset-y-0 left-0 z-30 w-72 h-full glass-panel transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 border-r border-white/5",
                isSidebarOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                <div className="flex flex-col h-full bg-[rgba(15,23,42,0.8)]">
                    <div className="p-6 border-b border-white/5 flex items-center justify-between">
                        <h1 className="font-bold text-2xl bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent flex items-center gap-3 tracking-wide">
                            <MessageSquare className="w-6 h-6 text-blue-400" />
                            TodoBot
                        </h1>
                        {onClose ? (
                            <button onClick={onClose} className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-full transition-all">
                                <X className="w-5 h-5" />
                            </button>
                        ) : (
                            <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden p-2 text-gray-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        )}
                    </div>

                    <div className="p-4">
                        <button
                            onClick={startNewChat}
                            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white py-3 px-4 rounded-xl font-medium transition-all shadow-lg shadow-blue-500/20 active:scale-95 neon-border"
                        >
                            <Plus className="w-5 h-5" />
                            New Chat
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1.5 custom-scrollbar">
                        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-2">History</div>
                        {loadingConversations ? (
                            <div className="flex justify-center p-4"><Loader2 className="animate-spin text-blue-400" /></div>
                        ) : conversations.length === 0 ? (
                            <div className="text-center text-gray-600 text-sm py-12 px-6 italic">No conversations yet</div>
                        ) : (
                            conversations.map(conv => (
                                <div
                                    key={conv.id}
                                    onClick={() => loadConversation(conv.id)}
                                    className={cn(
                                        "group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all border border-transparent",
                                        conversationId === conv.id
                                            ? "bg-blue-500/10 border-blue-500/20 text-blue-100 shadow-sm"
                                            : "hover:bg-white/5 text-gray-400 hover:text-gray-200"
                                    )}
                                >
                                    <div className="flex-1 truncate pr-3">
                                        <div className="font-medium truncate text-sm">
                                            {conv.title || "New Conversation"}
                                        </div>
                                        <div className="text-[10px] text-gray-500 mt-1 truncate font-mono opacity-70">
                                            {new Date(conv.updated_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => deleteConversation(e, conv.id)}
                                        className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/20 hover:text-red-400 rounded-md transition-all scale-90 hover:scale-100"
                                    >
                                        <Trash2 className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </aside>

            {/* Main Chat Area */}
            <main className="flex-1 flex flex-col h-full w-full relative bg-[var(--bg-primary)]">
                {/* Header */}
                <header className="h-16 border-b border-white/5 bg-[rgba(15,23,42,0.8)] backdrop-blur-md flex items-center px-6 justify-between lg:justify-end sticky top-0 z-10 shadow-sm">
                    <button
                        onClick={() => setIsSidebarOpen(true)}
                        className="lg:hidden p-2 -ml-2 text-gray-400 hover:bg-white/5 rounded-md transition-colors"
                    >
                        <Menu className="w-6 h-6" />
                    </button>
                    <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                        <div className="text-xs font-medium text-gray-400 uppercase tracking-widest">
                            {conversationId ? "Active Session" : "Ready"}
                        </div>
                    </div>
                    {onClose && (
                        <button onClick={onClose} className="ml-6 lg:hidden p-2 text-gray-400 hover:text-white transition-colors">
                            <X className="w-6 h-6" />
                        </button>
                    )}
                </header>

                {/* Messages List */}
                <div className="flex-1 overflow-y-auto p-4 lg:p-8 space-y-6 scroll-smooth custom-scrollbar">
                    {messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-center p-8 animate-in fade-in zoom-in-95 duration-500">
                            <div className="w-24 h-24 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-3xl flex items-center justify-center mb-8 shadow-2xl shadow-blue-900/20 border border-white/5 backdrop-blur-sm">
                                <MessageSquare className="w-12 h-12 text-blue-400" />
                            </div>
                            <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent mb-3">
                                How can I help you today?
                            </h2>
                            <p className="text-gray-500 max-w-md text-sm leading-relaxed">
                                I'm your AI Task Manager. Ask me to create tasks, manage your schedule, or organize your day.
                            </p>
                        </div>
                    ) : (
                        <div className="max-w-4xl mx-auto w-full pb-4 space-y-6">
                            <AnimatePresence initial={false}>
                                {messages.map((msg) => (
                                    <MessageBubble
                                        key={msg.id}
                                        role={msg.role}
                                        content={msg.content}
                                        toolsUsed={msg.tools_used}
                                        timestamp={msg.timestamp}
                                    />
                                ))}
                            </AnimatePresence>
                            {isLoading && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="flex justify-start mb-4 pl-2"
                                >
                                    <div className="bg-white/5 border border-white/10 rounded-2xl rounded-bl-none px-5 py-4 shadow-lg flex items-center gap-3 backdrop-blur-sm">
                                        <div className="flex space-x-1.5">
                                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-0" />
                                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-150" />
                                            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-300" />
                                        </div>
                                        <span className="text-xs text-gray-400 font-medium tracking-wide">AI IS THINKING...</span>
                                    </div>
                                </motion.div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-6 bg-[rgba(15,23,42,0.9)] border-t border-white/5 backdrop-blur-md sticky bottom-0 z-20">
                    <div className="max-w-4xl mx-auto relative group">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl opacity-20 group-hover:opacity-40 transition duration-500 blur"></div>
                        <div className="relative flex bg-[#0f172a] rounded-2xl">
                            <textarea
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Type your message..."
                                className="w-full bg-transparent text-gray-100 placeholder-gray-500 rounded-2xl pl-5 pr-14 py-4 focus:outline-none resize-none min-h-[60px] max-h-40 custom-scrollbar text-sm leading-relaxed"
                                rows={1}
                                disabled={isLoading}
                                style={{ minHeight: '60px' }}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={!inputValue.trim() || isLoading}
                                className="absolute right-2 bottom-2 p-2.5 bg-blue-600/90 text-white rounded-xl hover:bg-blue-500 disabled:opacity-30 disabled:hover:bg-blue-600/90 transition-all shadow-lg shadow-blue-500/20"
                            >
                                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                            </button>
                        </div>
                    </div>
                    <div className="text-center mt-3 text-[10px] text-gray-600 font-mono tracking-tight opacity-50">
                        AI can make mistakes. Design by Agent Antigravity.
                    </div>
                </div>
            </main>
        </div>
    );
}
