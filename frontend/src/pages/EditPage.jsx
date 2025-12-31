import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { videoAPI } from '../services/api';

function EditPage() {
  const { videoId } = useParams();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState(null);
  const [status, setStatus] = useState(null);
  const [headline, setHeadline] = useState('');
  const [location, setLocation] = useState('');
  const [showLocation, setShowLocation] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState('template1');
  const [rendering, setRendering] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [videoId]);

  const fetchData = async () => {
    try {
      const [analysisData, statusData] = await Promise.all([
        videoAPI.getAnalysis(videoId),
        videoAPI.getVideoStatus(videoId)
      ]);

      setAnalysis(analysisData);
      setStatus(statusData);
      setHeadline(analysisData.headline?.primary || '');
      setLocation(analysisData.location?.text || '');
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load video data');
      setLoading(false);
    }
  };

  const handleRender = async () => {
    setRendering(true);
    setError(null);

    try {
      // Update metadata
      await videoAPI.updateMetadata(videoId, {
        headline,
        location,
        show_location: showLocation
      });

      // Trigger render
      await videoAPI.triggerRender(videoId, {
        headline,
        location,
        show_location: showLocation,
        template_id: selectedTemplate
      });

      // Poll for completion
      pollRenderStatus();
    } catch (err) {
      setError(err.response?.data?.detail || 'Rendering failed');
      setRendering(false);
    }
  };

  const pollRenderStatus = () => {
    const interval = setInterval(async () => {
      try {
        const statusData = await videoAPI.getVideoStatus(videoId);

        if (statusData.status === 'completed') {
          clearInterval(interval);
          setRendering(false);
          setStatus(statusData);
        } else if (statusData.status === 'error') {
          clearInterval(interval);
          setError(statusData.error);
          setRendering(false);
        }
      } catch (err) {
        clearInterval(interval);
        setError('Failed to check render status');
        setRendering(false);
      }
    }, 3000);
  };

  const handleDownload = () => {
    const downloadURL = videoAPI.getDownloadURL(videoId);
    window.open(downloadURL, '_blank');
  };

  const handleRegenerateAI = async () => {
    setRegenerating(true);
    setError(null);

    try {
      // Trigger regeneration
      await videoAPI.regenerateAISuggestions(videoId);

      // Poll for updated suggestions
      let attempts = 0;
      const maxAttempts = 10;

      const pollInterval = setInterval(async () => {
        attempts++;

        try {
          const updatedAnalysis = await videoAPI.getAnalysis(videoId);

          // Update state with new suggestions
          setAnalysis(updatedAnalysis);
          setHeadline(updatedAnalysis.headline?.primary || '');
          setLocation(updatedAnalysis.location?.text || '');
          setRegenerating(false);
          clearInterval(pollInterval);
        } catch (err) {
          if (attempts >= maxAttempts) {
            clearInterval(pollInterval);
            setError('Failed to get updated suggestions');
            setRegenerating(false);
          }
        }
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to regenerate suggestions');
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading video data...</p>
      </div>
    );
  }

  if (error && !analysis) {
    return (
      <div className="max-w-4xl mx-auto">
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

  const isCompleted = status?.status === 'completed';

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Preview */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Preview</h2>

          {/* Video Preview Placeholder */}
          <div className="bg-gray-900 rounded-lg aspect-[9/16] flex items-center justify-center mb-4">
            <div className="text-center text-white">
              <svg
                className="mx-auto h-16 w-16 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-sm">9:16 Video Preview</p>
              <p className="text-xs text-gray-400 mt-1">{videoId}</p>
            </div>
          </div>

          {/* Download Button */}
          {isCompleted && (
            <button
              onClick={handleDownload}
              className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download Processed Video
            </button>
          )}
        </div>

        {/* Right Column - Edit */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Edit Details</h2>

          {/* Transcript */}
          {analysis?.transcript?.text && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Transcript</h3>
              <div className="bg-gray-50 rounded-md p-4 max-h-32 overflow-y-auto">
                <p className="text-sm text-gray-600">{analysis.transcript.text}</p>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Language: {analysis.transcript.language} (confidence: {(analysis.transcript.language_confidence * 100).toFixed(0)}%)
              </p>
            </div>
          )}

          {/* Template Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Choose Template
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setSelectedTemplate('template1')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedTemplate === 'template1'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">🎨</div>
                  <div className="text-xs font-medium text-gray-900">Template 1</div>
                  <div className="text-xs text-gray-500 mt-1">Full Frame Golden</div>
                </div>
              </button>

              <button
                onClick={() => setSelectedTemplate('template2')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedTemplate === 'template2'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">📺</div>
                  <div className="text-xs font-medium text-gray-900">Template 2</div>
                  <div className="text-xs text-gray-500 mt-1">Split Video Orange</div>
                </div>
              </button>

              <button
                onClick={() => setSelectedTemplate('template3')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedTemplate === 'template3'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">✨</div>
                  <div className="text-xs font-medium text-gray-900">Template 3</div>
                  <div className="text-xs text-gray-500 mt-1">Minimal Modern</div>
                </div>
              </button>

              <button
                onClick={() => setSelectedTemplate('template4')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedTemplate === 'template4'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">🏛️</div>
                  <div className="text-xs font-medium text-gray-900">Template 4</div>
                  <div className="text-xs text-gray-500 mt-1">Tiruvarur Updates</div>
                </div>
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Selected: <span className="font-medium">
                {selectedTemplate === 'template1' && 'Full Frame Golden - Top bar, date, logo, golden theme'}
                {selectedTemplate === 'template2' && 'Split Video Orange - News broadcast style, orange theme'}
                {selectedTemplate === 'template3' && 'Minimal Modern - Clean, simple design'}
                {selectedTemplate === 'template4' && 'Tiruvarur Updates - Red/maroon gradient, professional news style'}
              </span>
            </p>
          </div>

          {/* Headline Editor */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">
                Headline *
              </label>
              {analysis?.headline?.confidence && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  ✨ AI Suggested ({(analysis.headline.confidence * 100).toFixed(0)}%)
                </span>
              )}
            </div>
            <input
              type="text"
              value={headline}
              onChange={(e) => setHeadline(e.target.value)}
              maxLength={25}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Short, catchy headline..."
            />
            <div className="flex justify-between mt-1">
              <p className="text-xs text-gray-500">
                Keep it short and engaging!
              </p>
              <p className="text-xs text-gray-500">{headline.length}/25</p>
            </div>

            {/* Alternative Headlines */}
            {analysis?.headline?.alternatives?.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-gray-700 mb-2">Suggestions:</p>
                <div className="space-y-2">
                  {analysis.headline.alternatives.map((alt, index) => (
                    <button
                      key={index}
                      onClick={() => setHeadline(alt)}
                      className="w-full text-left px-3 py-2 text-sm bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
                    >
                      {alt}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Location Editor */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">
                  Location
                </label>
                {analysis?.location?.confidence && (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    ✨ AI ({(analysis.location.confidence * 100).toFixed(0)}%)
                  </span>
                )}
              </div>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={showLocation}
                  onChange={(e) => setShowLocation(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-600">Show on video</span>
              </label>
            </div>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              maxLength={25}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="City or Location"
            />
            <p className="text-xs text-gray-500 mt-1">
              {location.length}/25 characters
            </p>
          </div>

          {/* Regenerate AI Suggestions Button */}
          <div className="mb-6">
            <button
              onClick={handleRegenerateAI}
              disabled={regenerating}
              className="w-full flex justify-center items-center py-2 px-4 border border-purple-300 rounded-md shadow-sm text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              {regenerating ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-purple-700"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Regenerating AI Suggestions...
                </>
              ) : (
                <>
                  <svg
                    className="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  Regenerate AI Suggestions
                </>
              )}
            </button>
            <p className="text-xs text-gray-500 text-center mt-1">
              Get fresh headline and location suggestions from AI
            </p>
          </div>

          {/* Visual Analysis */}
          {analysis?.visual_analysis && analysis.visual_analysis.scene_type !== 'unknown' && (
            <div className="mb-6 p-4 bg-gray-50 rounded-md">
              <h3 className="text-sm font-medium text-gray-700 mb-2">AI Analysis</h3>
              <div className="space-y-1 text-sm text-gray-600">
                <p><span className="font-medium">Scene:</span> {analysis.visual_analysis.scene_type}</p>
                <p><span className="font-medium">Mood:</span> {analysis.visual_analysis.mood}</p>
                {analysis.visual_analysis.objects?.length > 0 && (
                  <p><span className="font-medium">Objects:</span> {analysis.visual_analysis.objects.join(', ')}</p>
                )}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Render Button */}
          {!isCompleted && (
            <button
              onClick={handleRender}
              disabled={!headline || rendering}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {rendering ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Rendering... (this may take 1-3 minutes)
                </>
              ) : (
                'Generate 9:16 Video'
              )}
            </button>
          )}

          {isCompleted && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-md">
              <p className="text-sm font-medium text-green-900">Video Ready!</p>
              <p className="text-sm text-green-700 mt-1">
                Your 9:16 video with text overlays is ready to download.
              </p>
            </div>
          )}

          {/* Back Button */}
          <button
            onClick={() => navigate('/')}
            className="w-full mt-4 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Upload New Video
          </button>
        </div>
      </div>
    </div>
  );
}

export default EditPage;
