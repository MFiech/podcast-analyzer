# Langfuse Integration

This document describes the Langfuse integration added to the podcast summarizer for LLM observability and evaluation.

## Overview

Langfuse has been integrated to provide comprehensive tracing and observability for all LLM calls in the podcast summarizer. This enables:

- **Tracing**: Track all LLM calls with detailed metadata
- **Evaluation**: Evaluate and optimize LLM performance
- **Cost Tracking**: Monitor token usage and costs
- **Debugging**: Debug issues with detailed call information

## Integration Details

### Files Modified

1. **`summarizer.py`** - Added Langfuse tracing to the `PodcastSummarizer.summarize()` method
2. **`cleaner.py`** - Added Langfuse tracing to the `TranscriptCleaner.clean_transcript()` method  
3. **`tasks.py`** - Added session-level tracing for complete episode analysis workflows
4. **`requirements.txt`** - Added `langfuse` dependency

### New Files

1. **`.env`** - Contains Langfuse credentials (not committed to git)
2. **`.env.example`** - Template for environment variables
3. **`test_langfuse_simple.py`** - Simple test script to verify integration

## Configuration

### Environment Variables

The following environment variables are required:

```bash
# Langfuse Configuration
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_HOST=http://localhost:4000

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

### Langfuse Server

Make sure your Langfuse server is running at `http://localhost:4000`. You can:

1. Use the cloud version at `https://cloud.langfuse.com`
2. Self-host Langfuse locally
3. Use the provided credentials for the local instance

## Usage

### Running with Tracing

The integration is automatic - no code changes needed when running your normal workflows:

```bash
# Activate virtual environment
source venv/bin/activate

# Run your normal podcast analysis
python -m celery -A celery_app worker --loglevel=info
```

### Viewing Traces

1. Open your Langfuse dashboard at `http://localhost:4000`
2. Navigate to the "Traces" section
3. View detailed information about each LLM call including:
   - Input/output content
   - Token usage and costs
   - Processing times
   - Metadata (episode titles, transcript lengths, etc.)

## Trace Structure

### Session-Level Traces

- **`podcast_episode_analysis`** - Complete episode processing workflow
- **`podcast_episode_resummarization`** - Re-summarization workflow

### Generation-Level Traces

- **`transcript_cleaning`** - Individual transcript cleaning calls
- **`podcast_summarization`** - Individual summarization calls

### Metadata Included

Each trace includes rich metadata:

- Episode title and URL
- Transcript length and word count
- Estimated and actual token usage
- Processing times
- Task IDs for Celery tasks

## Testing

Run the simple test to verify the integration:

```bash
source venv/bin/activate
python test_langfuse_simple.py
```

This will test:
- Langfuse imports and initialization
- Decorator functionality
- File syntax validation
- Environment variable loading

## Benefits

1. **Observability**: See exactly what's happening with your LLM calls
2. **Optimization**: Identify slow or expensive calls
3. **Debugging**: Debug issues with detailed call information
4. **Evaluation**: Compare different prompts and models
5. **Cost Tracking**: Monitor and optimize token usage

## Next Steps

1. Set your `OPENAI_API_KEY` in the `.env` file
2. Start your Langfuse server
3. Run your normal podcast analysis tasks
4. View traces in the Langfuse dashboard
5. Use the data to optimize your prompts and workflows

## Troubleshooting

### Common Issues

1. **"No module named 'langfuse'"** - Make sure you're in the virtual environment
2. **"Authentication error"** - Check your Langfuse credentials in `.env`
3. **"Connection refused"** - Make sure your Langfuse server is running
4. **"No traces visible"** - Check that `langfuse.flush()` is being called

### Getting Help

- Check the [Langfuse documentation](https://langfuse.com/docs)
- Review the test script for examples
- Check the console output for error messages
