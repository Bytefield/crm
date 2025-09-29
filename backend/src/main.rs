mod config;

use axum::{
    routing::get,
    Router,
    response::Json,
    extract::Extension,
};
use std::net::SocketAddr;
use tokio::net::TcpListener;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use sqlx::postgres::PgPoolOptions;
use crate::config::Config;

#[derive(serde::Serialize)]
struct HealthCheck {
    status: &'static str,
    database: &'static str,
}

// Add the root handler function
async fn root() -> &'static str {
    "Welcome to the CRM API"
}

// Add the health check handler function
async fn health_check(
    Extension(pool): Extension<sqlx::PgPool>,
) -> impl axum::response::IntoResponse {
    // Check database connection
    let db_status = sqlx::query("SELECT 1")
        .execute(&pool)
        .await
        .map(|_| "connected")
        .unwrap_or_else(|_| "disconnected");

    Json(HealthCheck { 
        status: "ok",
        database: db_status,
    })
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load configuration
    let config = Config::from_env()?;

    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(&config.log_level))
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Set up database connection pool
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&config.database_url)
        .await?;

    tracing::info!("Connected to database");

    // Run migrations
    sqlx::migrate!("../../migrations")
        .run(&pool)
        .await?;

    // Build our application with routes
    let app = Router::new()
        .route("/", get(root))
        .route("/health", get(health_check))
        .layer(Extension(pool));

    // Create a TcpListener
    let addr = SocketAddr::new(config.host.parse()?, config.port);
    let listener = TcpListener::bind(addr).await?;
    
    tracing::info!("Server listening on {}", addr);

    // Run the server
    axum::serve(listener, app).await?;
    
    Ok(())
}