import { Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import StatusPage from './pages/StatusPage';
import EditPage from './pages/EditPage';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Video Template Generator
          </h1>
          <p className="text-sm text-gray-600">
            AI-powered video processing for social media
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/status/:videoId" element={<StatusPage />} />
          <Route path="/edit/:videoId" element={<EditPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Powered by Gemini AI & FFmpeg
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
