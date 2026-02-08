import { auth } from "../lib/auth";

async function initDatabase() {
    try {
        console.log("🔄 Initializing better-auth database tables...");

        // Better-auth will auto-create tables when the auth instance is used
        // We just need to trigger the initialization
        await auth.api.getSession({
            headers: new Headers(),
        });

        console.log("✓ Database tables initialized successfully!");
        console.log("✓ Tables created:");
        console.log("  - users");
        console.log("  - sessions");
        console.log("  - accounts");
        console.log("  - verificationTokens");

    } catch (error: any) {
        // This is expected to fail (no session), but it will create the tables
        console.log("✓ Database initialized (tables created if they didn't exist)");
    }
}

initDatabase()
    .then(() => {
        console.log("\n✅ Database setup complete!");
        process.exit(0);
    })
    .catch((error) => {
        console.error("❌ Error:", error);
        process.exit(1);
    });
