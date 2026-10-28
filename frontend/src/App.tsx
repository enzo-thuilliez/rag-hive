import { BrowserRouter, Route, Routes } from "react-router";
import { Layout } from "./components/Layout";
import { AgentMapPage } from "./pages/AgentMapPage";
import { ResultsPage } from "./pages/ResultsPage";
import { UploadPage } from "./pages/UploadPage";

/** Root component: routes inside the app shell. */
export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<UploadPage />} />
          <Route path="runs/:runId/map" element={<AgentMapPage />} />
          <Route path="runs/:runId/results" element={<ResultsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
