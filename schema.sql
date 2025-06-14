CREATE TABLE transactions (
    transaction_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    filename TEXT NOT NULL,
    stored_path_original TEXT NOT NULL,
    stored_path_converted TEXT,
    original_format VARCHAR(10),
    original_codec VARCHAR(20),
    target_format VARCHAR(10),
    target_codec VARCHAR(20),
    status TEXT CHECK (status IN ('Pending', 'Converting', 'Completed', 'Failed', 'Retrying')),
    error_reason TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);