import React, { useState, useEffect } from 'react';

/**
 * Syntharra Option A: Diagnosis Dashboard
 * 
 * UI for displaying detected issues, proposed fixes, and manual approval buttons.
 * 
 * Features:
 * - Real-time issue list (sorted by severity)
 * - Proposed fix display (human-readable)
 * - Three action buttons per issue: "Fix It", "Skip", "Investigate"
 * - Status updates (loading, pending, testing, deployed, failed)
 * - Cost tracking and approval gates
 */

export default function DiagnosisDashboard() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [issueStatuses, setIssueStatuses] = useState({});
  const [testResults, setTestResults] = useState({});
  const [deploymentStatus, setDeploymentStatus] = useState(null);

  // Fetch list of agents on mount
  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const resp = await fetch('/api/agents');
      const data = await resp.json();
      setAgents(data.agents || []);
      if (data.agents?.length > 0) {
        setSelectedAgent(data.agents[0].agent_id);
      }
    } catch (err) {
      console.error('Failed to fetch agents:', err);
    }
  };

  const runDiagnosis = async (agentId) => {
    setLoading(true);
    try {
      const resp = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId })
      });
      const data = await resp.json();
      setIssues(data.issues || []);
      setIssueStatuses({}); // Reset statuses
    } catch (err) {
      console.error('Diagnosis failed:', err);
      setIssues([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFixIt = async (issueType, issueId) => {
    setIssueStatuses(prev => ({
      ...prev,
      [issueId]: 'testing'
    }));

    try {
      const resp = await fetch('/api/test-fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: selectedAgent,
          issue_type: issueType,
          issue_id: issueId
        })
      });
      const data = await resp.json();

      if (data.test_passed) {
        setTestResults(prev => ({
          ...prev,
          [issueId]: { status: 'passed', result: data }
        }));
        setIssueStatuses(prev => ({
          ...prev,
          [issueId]: 'ready_to_deploy'
        }));
      } else {
        setTestResults(prev => ({
          ...prev,
          [issueId]: { status: 'failed', result: data }
        }));
        setIssueStatuses(prev => ({
          ...prev,
          [issueId]: 'test_failed'
        }));
      }
    } catch (err) {
      console.error('Test failed:', err);
      setIssueStatuses(prev => ({
        ...prev,
        [issueId]: 'error'
      }));
    }
  };

  const handleDeploy = async (issueId) => {
    setDeploymentStatus('deploying');
    try {
      const resp = await fetch('/api/deploy-fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          issue_id: issueId,
          target: 'standard'  // or 'premium' or 'specific'
        })
      });
      const data = await resp.json();

      if (data.success) {
        setDeploymentStatus('success');
        setIssueStatuses(prev => ({
          ...prev,
          [issueId]: 'deployed'
        }));
        setTimeout(() => setDeploymentStatus(null), 3000);
      } else {
        setDeploymentStatus('failed');
      }
    } catch (err) {
      console.error('Deployment failed:', err);
      setDeploymentStatus('failed');
    }
  };

  const handleSkip = (issueId) => {
    setIssueStatuses(prev => ({
      ...prev,
      [issueId]: 'skipped'
    }));
  };

  const handleInvestigate = (issueId) => {
    setIssueStatuses(prev => ({
      ...prev,
      [issueId]: 'investigating'
    }));
  };

  const severityColor = (severity) => {
    const colors = {
      'CRITICAL': '#dc2626',
      'HIGH': '#ea580c',
      'MEDIUM': '#eab308',
      'LOW': '#3b82f6'
    };
    return colors[severity] || '#6b7280';
  };

  const statusBadge = (status) => {
    const styles = {
      'pending': { bg: '#f3f4f6', text: '#374151', label: 'Pending Review' },
      'testing': { bg: '#fef3c7', text: '#92400e', label: 'Testing...' },
      'ready_to_deploy': { bg: '#dcfce7', text: '#166534', label: 'Ready to Deploy' },
      'test_failed': { bg: '#fee2e2', text: '#991b1b', label: 'Test Failed' },
      'deploying': { bg: '#fef3c7', text: '#92400e', label: 'Deploying...' },
      'deployed': { bg: '#dcfce7', text: '#166534', label: '✓ Deployed' },
      'skipped': { bg: '#f3f4f6', text: '#6b7280', label: 'Skipped' },
      'investigating': { bg: '#dbeafe', text: '#1e40af', label: 'Manual Investigation' },
      'error': { bg: '#fee2e2', text: '#991b1b', label: 'Error' }
    };
    const style = styles[status] || styles['pending'];
    return <span style={{ background: style.bg, color: style.text, padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>{style.label}</span>;
  };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#1f2937' }}>
          Syntharra Option A: Agent Diagnosis Dashboard
        </h1>
        <p style={{ color: '#6b7280', fontSize: '14px' }}>
          Manual approval system with test-first deployment. Scan agents for issues, test fixes, deploy when ready.
        </p>
      </div>

      {/* Agent Selector + Scan Button */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '32px', alignItems: 'center' }}>
        <select
          value={selectedAgent || ''}
          onChange={(e) => setSelectedAgent(e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid #d1d5db',
            fontSize: '14px'
          }}
        >
          <option value="">Select Agent...</option>
          {agents.map(agent => (
            <option key={agent.agent_id} value={agent.agent_id}>
              {agent.name} ({agent.agent_id})
            </option>
          ))}
        </select>

        <button
          onClick={() => selectedAgent && runDiagnosis(selectedAgent)}
          disabled={!selectedAgent || loading}
          style={{
            padding: '8px 16px',
            background: '#6C63FF',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
            fontWeight: 'bold',
            fontSize: '14px'
          }}
        >
          {loading ? 'Scanning...' : 'Run Diagnosis'}
        </button>
      </div>

      {/* Summary Cards */}
      {issues.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
          <div style={{ background: '#fee2e2', padding: '16px', borderRadius: '8px' }}>
            <div style={{ color: '#991b1b', fontWeight: 'bold', fontSize: '24px' }}>
              {issues.filter(i => i.severity === 'CRITICAL').length}
            </div>
            <div style={{ color: '#7f1d1d', fontSize: '12px' }}>CRITICAL</div>
          </div>
          <div style={{ background: '#fed7aa', padding: '16px', borderRadius: '8px' }}>
            <div style={{ color: '#92400e', fontWeight: 'bold', fontSize: '24px' }}>
              {issues.filter(i => i.severity === 'HIGH').length}
            </div>
            <div style={{ color: '#78350f', fontSize: '12px' }}>HIGH</div>
          </div>
          <div style={{ background: '#fef3c7', padding: '16px', borderRadius: '8px' }}>
            <div style={{ color: '#92400e', fontWeight: 'bold', fontSize: '24px' }}>
              {issues.filter(i => i.severity === 'MEDIUM').length}
            </div>
            <div style={{ color: '#78350f', fontSize: '12px' }}>MEDIUM</div>
          </div>
          <div style={{ background: '#dbeafe', padding: '16px', borderRadius: '8px' }}>
            <div style={{ color: '#1e40af', fontWeight: 'bold', fontSize: '24px' }}>
              {issues.length}
            </div>
            <div style={{ color: '#1e3a8a', fontSize: '12px' }}>TOTAL</div>
          </div>
        </div>
      )}

      {/* Deployment Status Alert */}
      {deploymentStatus && (
        <div style={{
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '24px',
          background: deploymentStatus === 'success' ? '#dcfce7' : '#fee2e2',
          color: deploymentStatus === 'success' ? '#166534' : '#991b1b',
          fontWeight: 'bold'
        }}>
          {deploymentStatus === 'deploying' && '⏳ Deploying to production agents...'}
          {deploymentStatus === 'success' && '✓ Deployment successful! Fix applied to all agents.'}
          {deploymentStatus === 'failed' && '✗ Deployment failed. Check logs.'}
        </div>
      )}

      {/* Issues List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {issues.length === 0 && !loading && (
          <div style={{ padding: '32px', textAlign: 'center', color: '#6b7280' }}>
            {selectedAgent ? 'Run a diagnosis to see issues.' : 'Select an agent and run diagnosis.'}
          </div>
        )}

        {issues.map((issue, idx) => {
          const issueId = `${issue.issue_type}_${idx}`;
          const status = issueStatuses[issueId] || 'pending';
          const testResult = testResults[issueId];

          return (
            <div
              key={issueId}
              style={{
                border: `2px solid ${severityColor(issue.severity)}`,
                borderRadius: '8px',
                padding: '20px',
                background: '#ffffff',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}
            >
              {/* Issue Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '8px' }}>
                    <div
                      style={{
                        background: severityColor(issue.severity),
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        minWidth: '70px',
                        textAlign: 'center'
                      }}
                    >
                      {issue.severity}
                    </div>
                    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#1f2937' }}>
                      {issue.description}
                    </h3>
                  </div>
                  <p style={{ margin: '4px 0', fontSize: '13px', color: '#6b7280' }}>
                    Found in <strong>{issue.frequency}</strong> call{issue.frequency !== 1 ? 's' : ''} • 
                    Affected: <strong>{issue.affected_agents.join(', ')}</strong>
                  </p>
                </div>
                {statusBadge(status)}
              </div>

              {/* Proposed Fix */}
              <div style={{ marginBottom: '16px', padding: '12px', background: '#f9fafb', borderLeft: '4px solid #6C63FF', borderRadius: '4px' }}>
                <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#6b7280', marginBottom: '4px' }}>Proposed Fix:</div>
                <div style={{ fontSize: '13px', color: '#1f2937', fontFamily: 'monospace', overflowX: 'auto' }}>
                  {issue.proposed_fix}
                </div>
              </div>

              {/* Test Result (if available) */}
              {testResult && (
                <div style={{
                  marginBottom: '16px',
                  padding: '12px',
                  background: testResult.status === 'passed' ? '#dcfce7' : '#fee2e2',
                  borderRadius: '4px',
                  fontSize: '13px',
                  color: testResult.status === 'passed' ? '#166534' : '#991b1b'
                }}>
                  <strong>{testResult.status === 'passed' ? '✓ Test Passed' : '✗ Test Failed'}</strong>
                  <div style={{ marginTop: '4px', fontSize: '12px' }}>
                    {testResult.result.message || 'Check test results in logs.'}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {status === 'pending' && (
                  <>
                    <button
                      onClick={() => handleFixIt(issue.issue_type, issueId)}
                      style={{
                        padding: '8px 16px',
                        background: '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        fontSize: '13px'
                      }}
                    >
                      Fix It
                    </button>
                    <button
                      onClick={() => handleSkip(issueId)}
                      style={{
                        padding: '8px 16px',
                        background: '#d1d5db',
                        color: '#374151',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        fontSize: '13px'
                      }}
                    >
                      Skip
                    </button>
                    <button
                      onClick={() => handleInvestigate(issueId)}
                      style={{
                        padding: '8px 16px',
                        background: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        fontSize: '13px'
                      }}
                    >
                      Investigate Manually
                    </button>
                  </>
                )}

                {status === 'ready_to_deploy' && (
                  <>
                    <button
                      onClick={() => handleDeploy(issueId)}
                      style={{
                        padding: '8px 16px',
                        background: '#6C63FF',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        fontSize: '13px'
                      }}
                    >
                      Deploy to Production
                    </button>
                    <button
                      onClick={() => handleSkip(issueId)}
                      style={{
                        padding: '8px 16px',
                        background: '#d1d5db',
                        color: '#374151',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        fontSize: '13px'
                      }}
                    >
                      Rollback
                    </button>
                  </>
                )}

                {status === 'test_failed' && (
                  <button
                    onClick={() => handleFixIt(issue.issue_type, issueId)}
                    style={{
                      padding: '8px 16px',
                      background: '#f97316',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      fontSize: '13px'
                    }}
                  >
                    Retry Test
                  </button>
                )}

                {status === 'investigating' && (
                  <div style={{ fontSize: '13px', color: '#3b82f6', fontWeight: 'bold' }}>
                    👤 Manual investigation in progress...
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div style={{ marginTop: '48px', paddingTop: '24px', borderTop: '1px solid #e5e7eb', color: '#6b7280', fontSize: '12px' }}>
        <p>
          <strong>How it works:</strong> Diagnosis scans real call logs → You approve fixes → Test agent proves it works → Deploy to production with one click.
        </p>
        <p style={{ marginTop: '8px' }}>
          <strong>Cost:</strong> Scanning is free. Each test: $0.15. Deployment: free. No surprise bills — you control everything.
        </p>
      </div>
    </div>
  );
}
