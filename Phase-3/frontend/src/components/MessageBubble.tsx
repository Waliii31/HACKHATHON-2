'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { clsx } from 'clsx';
import { ToolUsage } from '@/types';
import { motion } from 'framer-motion';
import { Wrench, CheckCircle2, XCircle } from 'lucide-react';

interface MessageBubbleProps {
    role: 'user' | 'assistant';
    content: string;
    toolsUsed?: ToolUsage[];
    timestamp?: string;
}

export function MessageBubble({ role, content, toolsUsed, timestamp }: MessageBubbleProps) {
    const isUser = role === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx(
                "flex w-full mb-4",
                isUser ? "justify-end" : "justify-start"
            )}
        >
            <div className={clsx(
                "max-w-[80%] rounded-2xl px-4 py-3 shadow-sm",
                isUser
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-white border border-gray-100 text-gray-800 rounded-bl-none"
            )}>
                {/* Render Markdown Content */}
                <div className="prose prose-sm max-w-none break-words">
                    <ReactMarkdown
                        components={{
                            // Override paragraph styling to avoid excess margin if desired, 
                            // but default prose is usually okay.
                            // Make links open in new tab
                            a: ({ node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline" />
                        }}
                    >
                        {content}
                    </ReactMarkdown>
                </div>

                {/* Render Tool Usage Indicators */}
                {toolsUsed && toolsUsed.length > 0 && (
                    <div className="mt-3 space-y-2 pt-2 border-t border-gray-100/20">
                        {toolsUsed.map((tool, idx) => (
                            <div key={idx} className="flex items-center text-xs bg-black/5 p-1.5 rounded-md">
                                <Wrench className="w-3 h-3 mr-1.5 opacity-60" />
                                <span className="font-mono font-medium mr-2">{tool.name}</span>
                                {tool.success ? (
                                    <CheckCircle2 className="w-3 h-3 text-green-500 ml-auto" />
                                ) : (
                                    <XCircle className="w-3 h-3 text-red-500 ml-auto" />
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Timestamp */}
                {timestamp && (
                    <div className={clsx(
                        "text-[10px] mt-1 text-right opacity-60",
                        isUser ? "text-blue-100" : "text-gray-400"
                    )}>
                        {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                )}
            </div>
        </motion.div>
    );
}
