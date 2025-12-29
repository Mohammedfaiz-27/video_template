import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { videoAPI } from '../services/api';

function StatusPage() {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;

    const fetchStatus = async () => {
      try {
        const data = await videoAPI.getVideoStatus(videoId);
        setStatus(data);

        // If analyzed, redirect to edit page
        if (data.status === 'analyzed' || data.status === 'completed') {
          clearInterval(interval);
          setTimeout(() => {
            navigate(`/edit/${videoId}`);
          }, 1500);
        }

        // If error, stop polling
        if (data.status === 'error') {
          clearInterval(interval);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch status');
        clearInterval(interval);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 3 seconds
    interval = setInterval(fetchStatus, 3000);

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [videoId, navigate]);

  const getStatusColor = (currentStatus) => {
    switch (currentStatus) {
      case 'uploaded':
        return 'bg-blue-500';
      case 'analyzing':
        return 'bg-yellow-500';
      case 'analyzed':
        return 'bg-green-500';
      case 'rendering':
        return 'bg-purple-500';
      case 'completed':
        return 'bg-green-600';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (currentStatus) => {
    switch (currentStatus) {
      case 'uploaded':
        return '📤';
      case 'analyzing':
        return '🤖';
      case 'analyzed':
        return '✅';
      case 'rendering':
        return '🎬';
      case 'completed':
        return '🎉';
      case 'error':
        return '❌';
      default:
        return '⏳';
    }
  };

  const getStageMessage = (stage) => {
    switch (stage) {
      case 'upload':
        return 'Video uploaded successfully';
      case 'analysis':
        return 'Analyzing video with AI (this may take 30-60 seconds)';
      case 'render':
        return 'Rendering 9:16 video with text overlays';
      case 'finalizing':
        return 'Finalizing your video';
      case 'error':
        return 'An error occurred';
      default:
        return 'Processing...';
    }
  };

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-bold text-red-900 mb-2">Error</h2>
          <p className="text-red-700">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Upload New Video
          </button>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">{getStatusIcon(status.status)}</div>
          <h2 className="text-3xl font-bold text-gray-900 capitalize mb-2">
            {status.status}
          </h2>
          <p className="text-gray-600">{getStageMessage(status.stage)}</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{status.progress_percent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${getStatusColor(status.status)}`}
              style={{ width: `${status.progress_percent}%` }}
            ></div>
          </div>
        </div>

        {/* Timeline */}
        <div className="space-y-4">
          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              status.progress_percent >= 10 ? 'bg-green-500 text-white' : 'bg-gray-300'
            }`}>
              {status.progress_percent >= 10 ? '✓' : '1'}
            </div>
            <div className="ml-4">
              <p className="font-medium text-gray-900">Upload</p>
              <p className="text-sm text-gray-500">Video uploaded to server</p>
            </div>
          </div>

          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              status.progress_percent >= 70 ? 'bg-green-500 text-white' :
              status.progress_percent >= 40 ? 'bg-yellow-500 text-white animate-pulse' :
              'bg-gray-300'
            }`}>
              {status.progress_percent >= 70 ? '✓' : '2'}
            </div>
            <div className="ml-4">
              <p className="font-medium text-gray-900">AI Analysis</p>
              <p className="text-sm text-gray-500">
                Generating transcript, headline, and location
              </p>
            </div>
          </div>

          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              status.progress_percent >= 100 ? 'bg-green-500 text-white' :
              status.progress_percent >= 90 ? 'bg-purple-500 text-white animate-pulse' :
              'bg-gray-300'
            }`}>
              {status.progress_percent >= 100 ? '✓' : '3'}
            </div>
            <div className="ml-4">
              <p className="font-medium text-gray-900">Processing</p>
              <p className="text-sm text-gray-500">
                Converting to 9:16 and adding text overlays
              </p>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {status.error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm font-medium text-red-900">Error:</p>
            <p className="text-sm text-red-700 mt-1">{status.error}</p>
          </div>
        )}

        {/* Video ID */}
        <div className="mt-8 p-4 bg-gray-50 rounded-md">
          <p className="text-xs text-gray-500">Video ID</p>
          <p className="text-sm font-mono text-gray-700">{videoId}</p>
        </div>

        {/* Redirect Message */}
        {(status.status === 'analyzed' || status.status === 'completed') && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-700">
              Redirecting to preview page...
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default StatusPage;
