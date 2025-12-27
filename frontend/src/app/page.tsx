import Link from 'next/link';
import { ArrowRight, Mail, Calendar, Zap, Shield, Bot, Sparkles } from 'lucide-react';

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-slate-900/80 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold text-white">IntelliFlow</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <Link
                                href="/dashboard"
                                className="px-4 py-2 text-sm font-medium text-white/80 hover:text-white transition-colors"
                            >
                                Dashboard
                            </Link>
                            <Link
                                href="/auth/signin"
                                className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                            >
                                Sign In
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm mb-8">
                        <Bot className="w-4 h-4" />
                        <span>Powered by AI Agents</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                        Your Emails.
                        <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
                            Summarized & Actioned.
                        </span>
                    </h1>

                    <p className="text-xl text-white/60 max-w-3xl mx-auto mb-12">
                        IntelliFlow uses intelligent agents to summarize your emails, extract action items,
                        and automatically create calendar events. Powered by secure agent-to-agent communication.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            href="/auth/signin"
                            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold rounded-xl transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
                        >
                            Get Started Free
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                        <Link
                            href="#features"
                            className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-all border border-white/20"
                        >
                            Learn More
                        </Link>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            Two Agents. One Workflow.
                        </h2>
                        <p className="text-lg text-white/60 max-w-2xl mx-auto">
                            Our multi-agent system securely processes your emails and manages your calendar
                            using Descope-based OAuth authentication.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {/* Feature 1 */}
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-blue-500/50 transition-all group">
                            <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Mail className="w-6 h-6 text-blue-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Email Summarization</h3>
                            <p className="text-white/60">
                                Agent A fetches your emails and uses Claude AI to generate concise summaries
                                with extracted action items.
                            </p>
                        </div>

                        {/* Feature 2 */}
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-purple-500/50 transition-all group">
                            <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Calendar className="w-6 h-6 text-purple-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Calendar Integration</h3>
                            <p className="text-white/60">
                                Agent B receives delegated tokens and creates calendar events from
                                detected meetings and deadlines.
                            </p>
                        </div>

                        {/* Feature 3 */}
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-green-500/50 transition-all group">
                            <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Shield className="w-6 h-6 text-green-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Secure by Design</h3>
                            <p className="text-white/60">
                                OAuth 2.0 tokens with scoped permissions ensure agents only access
                                what they need. Delegation requires consent.
                            </p>
                        </div>

                        {/* Feature 4 */}
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-yellow-500/50 transition-all group">
                            <div className="w-12 h-12 rounded-xl bg-yellow-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Zap className="w-6 h-6 text-yellow-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Instant Processing</h3>
                            <p className="text-white/60">
                                Fast, async processing with Celery workers means your emails are
                                summarized in seconds, not minutes.
                            </p>
                        </div>

                        {/* Feature 5 */}
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-pink-500/50 transition-all group">
                            <div className="w-12 h-12 rounded-xl bg-pink-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Bot className="w-6 h-6 text-pink-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">LangGraph Agents</h3>
                            <p className="text-white/60">
                                Built with LangGraph for stateful, debuggable agent workflows
                                that handle complex email processing logic.
                            </p>
                        </div>

                        {/* Feature 6 */}
                        <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-cyan-500/50 transition-all group">
                            <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Sparkles className="w-6 h-6 text-cyan-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">Smart Detection</h3>
                            <p className="text-white/60">
                                AI detects meetings, deadlines, and action items with confidence
                                scores, so you never miss important events.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Architecture Section */}
            <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-white/10">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            How It Works
                        </h2>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8 relative">
                        {/* Step 1 */}
                        <div className="text-center">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                                1
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">Authenticate</h3>
                            <p className="text-white/60 text-sm">
                                Sign in with Descope and grant access to your Gmail and Calendar.
                            </p>
                        </div>

                        {/* Arrow */}
                        <div className="hidden md:flex items-center justify-center">
                            <ArrowRight className="w-8 h-8 text-white/20" />
                        </div>

                        {/* Step 2 */}
                        <div className="text-center md:col-start-2">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                                2
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">Process</h3>
                            <p className="text-white/60 text-sm">
                                Agent A summarizes emails and delegates calendar creation to Agent B.
                            </p>
                        </div>

                        {/* Step 3 */}
                        <div className="text-center md:col-start-3">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                                3
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-2">Act</h3>
                            <p className="text-white/60 text-sm">
                                View summaries, review action items, and see events on your calendar.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="p-8 md:p-12 rounded-3xl bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-white/10">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            Ready to streamline your inbox?
                        </h2>
                        <p className="text-lg text-white/60 mb-8">
                            Start using IntelliFlow today and let AI agents handle your email workflow.
                        </p>
                        <Link
                            href="/auth/signin"
                            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-slate-900 font-semibold rounded-xl hover:bg-white/90 transition-all"
                        >
                            Get Started Now
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-8 px-4 sm:px-6 lg:px-8 border-t border-white/10">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <span className="text-sm text-white/60">IntelliFlow © 2024</span>
                    </div>
                    <div className="text-sm text-white/40">
                        Built for the Descope Hackathon • Theme 3: Email Summarization + Calendar Action
                    </div>
                </div>
            </footer>
        </div>
    );
}
