import { WorkspaceClient } from './components/WorkspaceClient'

export default function WorkspacePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">工作區</h1>
          <p className="text-muted-foreground">
            管理和組織你的標籤，創建完美的 Prompt
          </p>
        </div>
        
        <WorkspaceClient />
      </div>
    </div>
  )
}
