// 그래프 인스턴스 전역 변수
let cy = null;
let serverCy = null; // 서버 그래프 인스턴스
let currentContainers = [];
let currentServers = []; // 현재 서버 목록

// 뷰 전환 함수
function switchView(viewType) {
  const serverView = document.getElementById('serverView');
  const serverGraphView = document.getElementById('serverGraphView');
  const statsSection = document.getElementById('statsSection');
  const toolbarSection = document.getElementById('toolbarSection');
  const serverBtn = document.getElementById('serverManagerBtn');
  const serverGraphBtn = document.getElementById('serverGraphBtn');

  // 모든 뷰 숨기기
  serverView.style.display = 'none';
  serverGraphView.style.display = 'none';
  
  // 모든 버튼 비활성화
  serverBtn.classList.remove('active');
  serverGraphBtn.classList.remove('active');

  if (viewType === 'server') {
    serverView.style.display = 'block';
    statsSection.style.display = 'none';
    toolbarSection.style.display = 'none';
    serverBtn.classList.add('active');
    
    // 서버 관리 뷰로 전환 시 서버 목록 자동 로드
    loadServerList();
  } else if (viewType === 'serverGraph') {
    serverGraphView.style.display = 'block';
    statsSection.style.display = 'none';
    toolbarSection.style.display = 'none';
    serverGraphBtn.classList.add('active');
    
    // 서버 그래프 뷰로 전환 시 서버 목록 로드 후 그래프 렌더링
    loadServerList().then(() => {
      setTimeout(() => {
        if (currentServers.length > 0) {
          renderServerGraph(currentServers);
        } else {
          const container = document.getElementById('serverCy');
          if (container) {
            container.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">서버 데이터를 불러오는 중...</div>';
          }
        }
      }, 100);
    });
  }
}

// 그래프 렌더링 함수
function renderGraph(containers) {
  const container = document.getElementById('cy');
  
  if (!container) {
    console.error('그래프 컨테이너를 찾을 수 없습니다.');
    return;
  }

  // 기존 그래프 제거
  if (cy) {
    cy.destroy();
    cy = null;
  }

  // 컨테이너가 없을 때 처리
  if (!containers || containers.length === 0) {
    container.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">컨테이너가 없습니다.</div>';
    return;
  }

  // Cytoscape가 로드되지 않았을 때 처리
  if (typeof cytoscape === 'undefined') {
    container.innerHTML = '<div style="padding: 20px; text-align: center; color: #f00;">Cytoscape.js 라이브러리를 로드할 수 없습니다.</div>';
    console.error('Cytoscape.js가 로드되지 않았습니다.');
    return;
  }

  // cytoscape-dagre 플러그인 등록 (사용 가능한 경우)
  if (typeof cytoscapeDagre !== 'undefined') {
    cytoscape.use(cytoscapeDagre);
  }

  // 상태 아이콘 매핑 함수
  function getStatusIcon(status) {
    const iconMap = {
      'running': '▶',
      'exited': '■',
      'created': '+',
      'restarting': '↻',
      'removing': '×',
      'paused': '⏸',
      'dead': '☠'
    };
    return iconMap[status?.toLowerCase()] || '?';
  }

  // 노드 데이터 생성
  const nodes = containers.map(c => ({
    data: {
      id: c.id,
      label: c.name || c.id.substring(0, 12),
      status: c.status,
      statusIcon: getStatusIcon(c.status),
      image: c.image,
      ports: c.ports,
      fullId: c.id
    }
  }));

  // 엣지 데이터 생성 (같은 네트워크에 있는 컨테이너 간 연결)
  // 실제로는 Docker 네트워크 정보를 기반으로 해야 하지만, 
  // 여기서는 예시로 모든 컨테이너를 중앙 노드에 연결
  const edges = [];
  const centerNodeId = 'center';
  
  // 중앙 노드 추가 (옵션)
  nodes.push({
    data: {
      id: centerNodeId,
      label: 'Docker Host',
      status: 'running',
      statusIcon: getStatusIcon('running'),
      isCenter: true
    }
  });

  // 각 컨테이너를 중앙에 연결
  containers.forEach(c => {
    edges.push({
      data: {
        id: `edge-${c.id}`,
        source: centerNodeId,
        target: c.id
      }
    });
  });

  try {
    // Cytoscape 초기화
    cy = cytoscape({
      container: container,
      elements: [...nodes, ...edges],
      style: [
        {
          selector: 'node',
          style: {
            'label': function(ele) {
              const icon = ele.data('statusIcon') || '?';
              const label = ele.data('label') || '';
              return `${icon} ${label}`;
            },
            'text-valign': 'center',
            'text-halign': 'center',
            'width': 'label',
            'height': 'label',
            'shape': 'roundrectangle',
            'min-width': '90px',
            'min-height': '70px',
            'padding': '12px',
            'background-color': '#F6F8FC',
            'border-width': '3px',
            'border-color': function(ele) {
              const status = ele.data('status');
              const borderColors = {
                'running': '#22C55E',      // 활발한 초록
                'exited': '#4C5D7A',       // Slate 600
                'created': '#3B82F6',      // Indigo Blue
                'restarting': '#EAB308',   // Golden Amber
                'removing': '#F87171',     // Soft Red
                'paused': '#FB923C',       // Warm Orange
                'dead': '#475569'          // Dark Slate
              };
              return borderColors[status?.toLowerCase()] || '#4C5D7A';
            },
            'color': '#1E2A3A',
            'font-size': function(ele) {
              // 노드 크기에 따라 폰트 크기 동적 계산
              const width = ele.width();
              const height = ele.height();
              const minSize = Math.min(width, height);
              // 최소 11px, 최대 16px, 노드 크기에 비례
              const fontSize = Math.max(11, Math.min(16, minSize * 0.15));
              return fontSize + 'px';
            },
            'font-weight': '600',
            'text-wrap': 'wrap',
            'text-max-width': function(ele) {
              // 노드 너비의 80%를 최대 텍스트 너비로 설정
              return (ele.width() * 0.8) + 'px';
            },
            'text-outline-width': 0,
            'text-outline-color': 'transparent',
            'text-background-color': 'transparent',
            'text-background-opacity': 0,
            'text-background-padding': '0px',
            'text-background-shape': 'roundrectangle',
            'text-border-width': 0,
            'text-border-color': 'transparent',
            'overlay-opacity': 0,
            'overlay-color': 'transparent',
            'overlay-padding': '0px'
          }
        },
        {
          selector: 'node[isCenter = true]',
          style: {
            'label': function(ele) {
              const icon = ele.data('statusIcon') || '?';
              const label = ele.data('label') || '';
              return `${icon} ${label}`;
            },
            'background-color': '#F6F8FC',
            'border-width': '3px',
            'border-color': '#475569',
            'color': '#1E2A3A',
            'width': 'label',
            'height': 'label',
            'min-width': '150px',
            'min-height': '90px',
            'shape': 'roundrectangle',
            'font-size': function(ele) {
              // 중앙 노드 크기에 따라 폰트 크기 동적 계산
              const width = ele.width();
              const height = ele.height();
              const minSize = Math.min(width, height);
              // 최소 13px, 최대 18px
              const fontSize = Math.max(13, Math.min(18, minSize * 0.12));
              return fontSize + 'px';
            },
            'font-weight': '700',
            'text-outline-width': 0,
            'text-outline-color': 'transparent'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#64748b',
            'line-style': 'solid',
            'target-arrow-shape': 'none',
            'curve-style': 'bezier',
            'opacity': 0.75,
            'source-endpoint': 'outside-to-node',
            'target-endpoint': 'outside-to-node'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': '2px',
            'border-color': '#6366f1',
            'border-style': 'solid',
            'z-index': 1000,
            'background-color': '#f0f4ff'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'opacity': 0.9,
            'line-color': '#6366f1',
            'width': 2.5
          }
        },
        {
          selector: 'node:hover',
          style: {
            'transition-property': 'width, height',
            'transition-duration': '0.2s',
            'transition-timing-function': 'ease-out'
          }
        }
      ],
    layout: (typeof cytoscapeDagre !== 'undefined') ? {
      name: 'dagre',
      rankDir: 'TB',
      spacingFactor: 1.1,
      nodeSep: 60,
      edgeSep: 30,
      rankSep: 100
    } : {
      name: 'breadthfirst',
      directed: true,
      spacingFactor: 1.1,
      padding: 20
    }
  });

  // 그래프 배경을 밝은 테마로 변경
  container.style.background = '#ffffff';

    // 호버 효과 (미니멀하게)
    cy.on('mouseover', 'node', function(evt) {
      const node = evt.target;
      if (!node.data('isCenter')) {
        // 현재 크기 기준으로 1.1배 확대
        const currentWidth = node.width();
        const currentHeight = node.height();
        const newWidth = currentWidth * 1.1;
        const newHeight = currentHeight * 1.1;
        
        node.style('width', newWidth + 'px');
        node.style('height', newHeight + 'px');
        node.style('z-index', 999);
        node.style('border-width', '4px');  // 호버 시 테두리 더 두껍게
        node.style('background-color', '#EEF2FB');
        
        // 폰트 크기도 함께 조정 (노드 크기에 반응)
        const minSize = Math.min(newWidth, newHeight);
        const fontSize = Math.max(11, Math.min(16, minSize * 0.15));
        node.style('font-size', fontSize + 'px');
        
        // 연결된 엣지 강조
        node.connectedEdges().style('opacity', 0.85);
        node.connectedEdges().style('width', 2.5);
        node.connectedEdges().style('line-color', '#475569');
      }
    });

    cy.on('mouseout', 'node', function(evt) {
      const node = evt.target;
      if (!node.data('isCenter')) {
        // 원래 크기로 복원 (label 기반으로 자동 조정)
        node.style('width', 'label');
        node.style('height', 'label');
        node.style('z-index', 0);
        node.style('border-width', '3px');  // 원래 테두리 두께로 복원
        node.style('background-color', '#F6F8FC');
        // 폰트 크기도 자동으로 조정됨 (font-size 함수가 다시 계산)
        
        // 엣지 원래 스타일로 복원
        node.connectedEdges().style('opacity', 0.75);
        node.connectedEdges().style('width', 2);
        node.connectedEdges().style('line-color', '#64748b');
      }
    });
    
    // 노드 선택 효과 및 정보 표시
    cy.on('tap', 'node', function(evt) {
      const node = evt.target;
      const data = node.data();
      
      if (data.isCenter) return;
      
      // 다른 노드 선택 해제
      cy.elements().removeClass('selected');
      // 현재 노드 선택
      node.addClass('selected');
      // 연결된 엣지 선택
      node.connectedEdges().addClass('selected');
      
      // 정보 표시
      const info = `
컨테이너 ID: ${data.fullId}
이름: ${data.label}
상태: ${data.status}
이미지: ${data.image}
포트: ${data.ports || 'N/A'}
      `.trim();
      
      alert(info);
    });

    console.log('그래프 렌더링 완료:', nodes.length, '노드,', edges.length, '엣지');
  } catch (error) {
    console.error('그래프 렌더링 오류:', error);
    container.innerHTML = '<div style="padding: 20px; text-align: center; color: #f00;">그래프를 렌더링하는 중 오류가 발생했습니다. 콘솔을 확인하세요.</div>';
  }
}

// 그래프 레이아웃 초기화
function resetGraphLayout() {
  if (cy) {
    const layoutName = (typeof cytoscapeDagre !== 'undefined') ? 'dagre' : 'breadthfirst';
    cy.layout({
      name: layoutName,
      rankDir: 'TB',
      spacingFactor: 1.1,
      nodeSep: 60,
      edgeSep: 30,
      rankSep: 100
    }).run();
  }
}

// 그래프 전체 보기
function fitGraph() {
  if (cy) {
    // 패딩 추가 및 최소 줌 레벨 설정
    cy.fit(undefined, 50);  // 50px 패딩 추가
    // 최소 줌 레벨 제한 (너무 작아지지 않도록)
    if (cy.zoom() < 0.5) {
      cy.zoom(0.5);
    }
  }
}

// ============================================
// 서버 그래프 렌더링 함수
// ============================================

// 서버 그래프 렌더링 함수
function renderServerGraph(servers) {
  const container = document.getElementById('serverCy');
  
  if (!container) {
    console.error('서버 그래프 컨테이너를 찾을 수 없습니다.');
    return;
  }

  // 기존 그래프 제거
  if (serverCy) {
    serverCy.destroy();
    serverCy = null;
  }

  // 서버가 없을 때 처리
  if (!servers || servers.length === 0) {
    container.innerHTML = `
      <div class="graph-empty-state">
        <i class="fas fa-server" style="font-size: 4rem; color: #9ca3af; margin-bottom: 1.5rem;"></i>
        <h3 style="font-size: 1.5rem; color: var(--text-primary); margin-bottom: 0.5rem; font-weight: 600;">등록된 서버가 없습니다</h3>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.875rem;">서버를 추가하여 연합학습 네트워크를 구성하세요.</p>
        <button class="btn-modern btn-primary" onclick="showAddServerForm()" style="margin-top: 0.5rem;">
          <i class="fas fa-plus"></i>
          <span>서버 추가</span>
        </button>
      </div>
    `;
    return;
  }

  // Cytoscape가 로드되지 않았을 때 처리
  if (typeof cytoscape === 'undefined') {
    container.innerHTML = '<div style="padding: 20px; text-align: center; color: #f00;">Cytoscape.js 라이브러리를 로드할 수 없습니다.</div>';
    console.error('Cytoscape.js가 로드되지 않았습니다.');
    return;
  }

  // cytoscape-dagre 플러그인 등록 (사용 가능한 경우)
  if (typeof cytoscapeDagre !== 'undefined') {
    cytoscape.use(cytoscapeDagre);
  }

  // 상태 아이콘 매핑 함수
  function getServerStatusIcon(status) {
    return status === 'online' ? '✓' : '✗';
  }

  // 중앙 서버와 클라이언트 서버 분리
  const centralServer = servers.find(s => s.role === 'central');
  const clientServers = servers.filter(s => s.role !== 'central');

  // 클라이언트 서버가 없을 때 처리 (실무 패턴: 조건부 빈 상태)
  if (clientServers.length === 0) {
    container.innerHTML = `
      <div class="graph-empty-state">
        <i class="fas fa-network-wired" style="font-size: 4rem; color: #9ca3af; margin-bottom: 1.5rem;"></i>
        <h3 style="font-size: 1.5rem; color: var(--text-primary); margin-bottom: 0.5rem; font-weight: 600;">서버 네트워크 구성 필요</h3>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.875rem; max-width: 400px; margin-left: auto; margin-right: auto;">
          클라이언트 서버를 추가하여 연합학습 네트워크를 구성하세요.<br>
          중앙 서버만으로는 네트워크를 시각화할 수 없습니다.
        </p>
        <button class="btn-modern btn-primary" onclick="showAddServerForm()" style="margin-top: 0.5rem;">
          <i class="fas fa-plus"></i>
          <span>클라이언트 서버 추가</span>
        </button>
      </div>
    `;
    return;
  }

  // 노드 데이터 생성
  const nodes = servers.map(s => ({
    data: {
      id: s.id,
      label: s.label || s.id,
      status: s.status,
      statusIcon: getServerStatusIcon(s.status),
      type: s.type || 'remote',
      role: s.role || 'client',
      fullId: s.id,
      base_url: s.base_url || '',
      isCentral: s.role === 'central'
    }
  }));

  // 엣지 생성: 중앙 서버 → 클라이언트 서버
  const edges = [];
  if (centralServer && clientServers.length > 0) {
    clientServers.forEach(client => {
      edges.push({
        data: {
          id: `edge-${centralServer.id}-${client.id}`,
          source: centralServer.id,
          target: client.id
        }
      });
    });
  }

  try {
    // Cytoscape 초기화
    serverCy = cytoscape({
      container: container,
      elements: [...nodes, ...edges],
      style: [
        {
          selector: 'node',
          style: {
            'label': function(ele) {
              const icon = ele.data('statusIcon') || '?';
              const label = ele.data('label') || '';
              return `${icon} ${label}`;
            },
            'text-valign': 'center',
            'text-halign': 'center',
            'width': 'label',
            'height': 'label',
            'shape': 'roundrectangle',
            'min-width': '140px',
            'min-height': '60px',
            'padding': '12px 16px',
            'background-color': '#FFFFFF',
            'border-width': '1px',
            'border-color': function(ele) {
              const status = ele.data('status');
              const role = ele.data('role');
              if (role === 'central') {
                return status === 'online' ? '#4B5563' : '#EA4335';
              }
              if (status === 'online') {
                return '#60A5FA'; // 연파랑 (기존: #34A853)
              } else if (status === 'offline') {
                return '#EA4335'; // Kubeflow 실패 테두리 (정확한 색상)
              }
              return '#9E9E9E'; // 대기 상태
            },
            'border-radius': '8px',
            'color': '#1F2937',
            'font-size': '13px',
            'font-weight': '500',
            'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'text-wrap': 'wrap',
            'text-max-width': '120px',
            'text-margin-y': '0px',
            'overlay-opacity': 0,
            'transition-property': 'border-width, border-color, background-color, transform',
            'transition-duration': '0.2s',
            'transition-timing-function': 'ease-in-out'
          }
        },
        {
          selector: 'node[isCentral = true]',
          style: {
            'label': function(ele) {
              const icon = ele.data('statusIcon') || '?';
              const label = ele.data('label') || '';
              return `${icon} ${label}`;
            },
            'background-color': '#FFFFFF',
            'border-width': '1.5px',
            'border-color': function(ele) {
              const status = ele.data('status');
              return status === 'online' ? '#4B5563' : '#EA4335';
            },
            'min-width': '160px',
            'min-height': '70px',
            'font-size': '14px',
            'font-weight': '600',
            'padding': '14px 18px'
          }
        },
        {
          selector: 'node:active',
          style: {
            'border-width': '1.5px',
            'transform': 'scale(0.98)',
            'transition-duration': '0.1s'
          }
        },
        {
          selector: 'node:hover',
          style: {
            'border-width': '1.5px',
            'border-color': function(ele) {
              const status = ele.data('status');
              const role = ele.data('role');
              if (role === 'central') {
                return status === 'online' ? '#4B5563' : '#EA4335';
              }
              if (status === 'online') {
                return '#60A5FA';
              } else if (status === 'offline') {
                return '#EA4335';
              }
              return '#9E9E9E';
            },
            'transition-duration': '0.15s',
            'box-shadow': '0 4px 12px rgba(0, 0, 0, 0.15)'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': '2px',
            'border-color': function(ele) {
              const status = ele.data('status');
              const role = ele.data('role');
              if (role === 'central') {
                return status === 'online' ? '#4B5563' : '#EA4335';
              }
              if (status === 'online') {
                return '#60A5FA';
              } else if (status === 'offline') {
                return '#EA4335';
              }
              return '#9E9E9E';
            },
            'background-color': '#FFFFFF',
            'z-index': 1000,
            'box-shadow': '0 6px 16px rgba(0, 0, 0, 0.2)'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1,
            'line-color': '#9CA3AF', // Kubeflow 기본 엣지 색상
            'line-style': 'solid',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#9CA3AF',
            'target-arrow-size': '8px',
            'target-arrow-fill': 'filled',
            'curve-style': 'bezier',
            'control-point-distances': [0, -20],
            'control-point-weights': [0.25, 0.75],
            'opacity': 0.6,
            'transition-property': 'width, line-color, opacity',
            'transition-duration': '0.2s'
          }
        },
        {
          selector: 'edge:hover',
          style: {
            'width': 1.5,
            'line-color': '#6366F1',
            'target-arrow-color': '#6366F1',
            'opacity': 0.9
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'width': 1.5,
            'line-color': '#6366F1',
            'target-arrow-color': '#6366F1',
            'opacity': 1
          }
        }
      ],
      layout: (typeof cytoscapeDagre !== 'undefined') ? {
        name: 'dagre',
        rankDir: 'TB',
        nodeSep: 80,
        edgeSep: 40,
        rankSep: 120,
        ranker: 'network-simplex',
        padding: 40
      } : {
        name: 'breadthfirst',
        directed: true,
        spacingFactor: 1.2,
        padding: 40,
        roots: centralServer ? `#${centralServer.id}` : undefined
      }
    });

    // 그래프 배경 설정 (Kubeflow 스타일)
    container.style.background = '#FAFBFC';
    container.style.border = '1px solid #E5E7EB';
    container.style.borderRadius = '8px';

    // 노드 클릭 이벤트
    serverCy.on('tap', 'node', function(evt) {
      const node = evt.target;
      const data = node.data();
      
      // 다른 노드 선택 해제
      serverCy.elements().removeClass('selected');
      // 현재 노드 선택
      node.addClass('selected');
      // 연결된 엣지 선택
      node.connectedEdges().addClass('selected');
      
      // 상세 정보 패널 표시
      showServerDetailsPanel(data);
    });

    // 배경 클릭 시 패널 닫기
    serverCy.on('tap', function(evt) {
      if (evt.target === serverCy) {
        serverCy.elements().removeClass('selected');
        closeServerDetailsPanel();
      }
    });

    console.log('서버 그래프 렌더링 완료:', nodes.length, '노드,', edges.length, '엣지');
  } catch (error) {
    console.error('서버 그래프 렌더링 오류:', error);
    container.innerHTML = '<div style="padding: 20px; text-align: center; color: #f00;">그래프를 렌더링하는 중 오류가 발생했습니다. 콘솔을 확인하세요.</div>';
  }
}

// 서버 그래프 레이아웃 초기화
function resetServerGraphLayout() {
  if (serverCy) {
    const centralNode = serverCy.nodes('[isCentral = true]');
    const layoutOptions = (typeof cytoscapeDagre !== 'undefined') ? {
      name: 'dagre',
      rankDir: 'TB',
      nodeSep: 80,
      edgeSep: 40,
      rankSep: 120,
      ranker: 'network-simplex',
      padding: 40
    } : {
      name: 'breadthfirst',
      directed: true,
      spacingFactor: 1.2,
      padding: 40,
      roots: centralNode.length > 0 ? `#${centralNode[0].id()}` : undefined
    };
    serverCy.layout(layoutOptions).run();
  }
}

// 서버 상세 정보 패널 표시
function showServerDetailsPanel(serverData) {
  const panel = document.getElementById('serverDetailsPanel');
  const content = document.getElementById('serverDetailsContent');
  
  if (!panel || !content) return;
  
  // 서버 정보 가져오기 (base_url 등 추가 정보)
  const server = currentServers.find(s => s.id === serverData.fullId) || serverData;
  
  const statusText = serverData.status === 'online' ? '온라인' : '오프라인';
  const roleText = serverData.role === 'central' ? '중앙 서버' : '클라이언트 서버';
  
  content.innerHTML = `
    <div class="detail-section">
      <h4><i class="fas fa-server"></i> 기본 정보</h4>
      <div class="detail-item">
        <span class="detail-label">서버 ID:</span>
        <span class="detail-value">${serverData.fullId}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">서버 이름:</span>
        <span class="detail-value">${serverData.label}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">상태:</span>
        <span class="detail-value status-${serverData.status}">
          <i class="fas ${serverData.status === 'online' ? 'fa-check-circle' : 'fa-times-circle'}"></i>
          ${statusText}
        </span>
      </div>
      <div class="detail-item">
        <span class="detail-label">역할:</span>
        <span class="detail-value role-${serverData.role}">
          <i class="fas ${serverData.role === 'central' ? 'fa-crown' : 'fa-desktop'}"></i>
          ${roleText}
        </span>
      </div>
    </div>
    <div class="detail-section">
      <h4><i class="fas fa-network-wired"></i> 연결 정보</h4>
      <div class="detail-item">
        <span class="detail-label">URL:</span>
        <span class="detail-value">${server.base_url || serverData.base_url || 'N/A'}</span>
      </div>
    </div>
  `;
  
  panel.style.display = 'block';
}

// 서버 상세 정보 패널 닫기
function closeServerDetailsPanel() {
  const panel = document.getElementById('serverDetailsPanel');
  if (panel) {
    panel.style.display = 'none';
  }
}

// 서버 그래프 전체 보기
function fitServerGraph() {
  if (serverCy) {
    serverCy.fit(undefined, 50);
    if (serverCy.zoom() < 0.5) {
      serverCy.zoom(0.5);
    }
  }
}

// 통계 업데이트 함수 (애니메이션 제거 - 안정성 향상)
function updateStats(containers) {
  const total = containers.length;
  const running = containers.filter(c => c.status.toLowerCase() === 'running').length;
  const stopped = Math.max(0, total - running); // 음수 방지

  // 즉시 최종 값 표시 (애니메이션 없음)
  document.getElementById('statTotal').textContent = total;
  document.getElementById('statRunning').textContent = running;
  document.getElementById('statStopped').textContent = stopped;
}

// 카드 렌더링 함수
function renderContainerCards(containers, nodeId) {
  const containerGrid = document.getElementById('containerGrid');
  
  if (!containers || containers.length === 0) {
    containerGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <i class="fas fa-inbox"></i>
        <h3>컨테이너가 없습니다</h3>
        <p>이 노드에 등록된 컨테이너가 없습니다.</p>
      </div>
    `;
    return;
  }

  containerGrid.innerHTML = '';
  
  containers.forEach((c, index) => {
    const card = document.createElement('div');
    card.className = `container-card ${c.status.toLowerCase()}`;
    card.style.animationDelay = `${index * 0.05}s`;
    
    const statusClassMap = {
      "running": "badge-running",
      "exited": "badge-exited",
      "created": "badge-created",
      "restarting": "badge-restarting",
      "removing": "badge-removing",
      "paused": "badge-paused",
      "dead": "badge-dead"
    };
    
    const statusClass = statusClassMap[c.status.toLowerCase()] || "badge-exited";
    const statusIconMap = {
      "running": "fa-play-circle",
      "exited": "fa-stop-circle",
      "created": "fa-plus-circle",
      "restarting": "fa-sync-alt",
      "removing": "fa-trash-alt",
      "paused": "fa-pause-circle",
      "dead": "fa-skull"
    };
    const statusIcon = statusIconMap[c.status.toLowerCase()] || "fa-question-circle";
    
    card.innerHTML = `
      <div class="card-header">
        <div>
          <div class="card-title">${c.name || 'Unnamed'}</div>
          <div class="card-id">${c.id}</div>
        </div>
        <span class="card-badge ${statusClass}">
          <i class="fas ${statusIcon}"></i> ${c.status}
        </span>
      </div>
      <div class="card-body">
        <div class="card-info">
          <i class="fas fa-image"></i>
          <span class="card-info-label">이미지:</span>
          <span class="card-info-value">${c.image || 'N/A'}</span>
        </div>
        ${c.ports ? `
        <div class="card-info">
          <i class="fas fa-network-wired"></i>
          <span class="card-info-label">포트:</span>
          <span class="card-info-value">${c.ports}</span>
        </div>
        ` : ''}
      </div>
      <div class="card-actions">
        <button class="btn-action start" onclick="doAction('start', '${nodeId}', '${c.id}')" ${c.status.toLowerCase() === 'running' ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
          <i class="fas fa-play"></i>
          <span>시작</span>
        </button>
        <button class="btn-action stop" onclick="doAction('stop', '${nodeId}', '${c.id}')" ${c.status.toLowerCase() !== 'running' ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
          <i class="fas fa-stop"></i>
          <span>중지</span>
        </button>
        <button class="btn-action restart" onclick="doAction('restart', '${nodeId}', '${c.id}')">
          <i class="fas fa-redo"></i>
          <span>재시작</span>
        </button>
      </div>
    `;
    
    containerGrid.appendChild(card);
  });
}

// 로딩 표시 함수
function showLoading() {
  document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
  document.getElementById('loadingOverlay').style.display = 'none';
}

async function reloadContainers() {
  const nodeSelect = document.getElementById("nodeSelect");
  const nodeId = nodeSelect.value;
  const containerGrid = document.getElementById("containerGrid");
  const statusText = document.getElementById("statusText");

  showLoading();
  containerGrid.innerHTML = '';
  statusText.textContent = "";

  try {
    const res = await fetch(`/api/containers?node_id=${encodeURIComponent(nodeId)}&all=true`);
    const data = await res.json();

    if (!Array.isArray(data)) {
      containerGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <i class="fas fa-exclamation-triangle"></i>
          <h3>데이터 형식 오류</h3>
          <p>서버에서 올바른 형식의 데이터를 받지 못했습니다.</p>
        </div>
      `;
      hideLoading();
      return;
    }

    // 전역 변수에 저장 (그래프에서 사용)
    currentContainers = data;

    // 통계 업데이트
    updateStats(data);

    // 카드 렌더링
    renderContainerCards(data, nodeId);

    // 그래프 뷰가 활성화되어 있으면 그래프도 업데이트
    if (document.getElementById('graphView').style.display !== 'none') {
      renderGraph(data);
    }

    const now = new Date();
    statusText.textContent = `노드: ${nodeId} · 컨테이너 ${data.length}개 · 갱신: ${now.toLocaleTimeString()}`;
    
    hideLoading();
  } catch (e) {
    console.error(e);
    containerGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <i class="fas fa-exclamation-circle"></i>
        <h3>불러오기 실패</h3>
        <p>컨테이너 정보를 불러오는 중 오류가 발생했습니다.</p>
      </div>
    `;
    statusText.textContent = "에러 발생 (콘솔 로그 참조)";
    hideLoading();
  }
}

async function doAction(action, nodeId, containerId) {
  const actionNames = {
    'start': '시작',
    'stop': '중지',
    'restart': '재시작'
  };
  
  if (!confirm(`${containerId} 컨테이너를 ${actionNames[action]} 하시겠습니까?`)) return;

  showLoading();

  try {
    const res = await fetch(`/api/containers/${action}`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        node_id: nodeId,
        container_id: containerId
      })
    });

    if (res.ok) {
      await reloadContainers();
      // 성공 메시지 (간단한 토스트)
      showToast(`${actionNames[action]} 요청이 완료되었습니다.`, 'success');
    } else {
      hideLoading();
      showToast(`${actionNames[action]} 요청이 실패했습니다.`, 'error');
    }
  } catch (e) {
    console.error(e);
    hideLoading();
    showToast('요청 중 오류가 발생했습니다.', 'error');
  }
}

// 간단한 토스트 알림
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 10000;
    animation: slideInRight 0.3s ease-out;
    font-weight: 500;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOutRight 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// 페이지 로드 시 기본 뷰를 서버 그래프로 설정
window.addEventListener("load", function() {
  switchView('serverGraph');
});

// ============================================
// 서버 관리 함수
// ============================================

let currentEditingServerId = null;

// 서버 관리 뷰 열기 (switchView로 대체됨, 호환성을 위해 유지)
async function openServerManager() {
  switchView('server');
}

// 서버 목록 로드
async function loadServerList() {
  try {
    const response = await fetch('/api/nodes/status');
    
    // HTTP 응답 상태 체크 추가
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch (e) {
        // JSON 파싱 실패 시 기본 메시지 사용
      }
      throw new Error(errorMessage);
    }
    
    const servers = await response.json();
    
    // 응답이 배열인지 확인
    if (!Array.isArray(servers)) {
      throw new Error('서버 목록 형식이 올바르지 않습니다');
    }
    
    // 전역 변수에 저장 (그래프에서 사용)
    currentServers = servers;
    
    const serverList = document.getElementById('serverList');
    if (!serverList) {
      // serverList가 없어도 그래프는 업데이트 가능
      // 서버 그래프 뷰가 활성화되어 있으면 그래프 업데이트
      if (document.getElementById('serverGraphView') && document.getElementById('serverGraphView').style.display !== 'none') {
        if (servers.length > 0) {
          renderServerGraph(servers);
        } else {
          const container = document.getElementById('serverCy');
          if (container) {
            container.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">등록된 서버가 없습니다.</div>';
          }
        }
      }
      return;
    }
    
    serverList.innerHTML = '';
    
    if (servers.length === 0) {
      serverList.innerHTML = '<div class="empty-state"><p>등록된 서버가 없습니다.</p></div>';
      // 서버 그래프 뷰가 활성화되어 있으면 그래프도 업데이트
      if (document.getElementById('serverGraphView') && document.getElementById('serverGraphView').style.display !== 'none') {
        renderServerGraph([]);
      }
      return;
    }
    
    servers.forEach(server => {
      const serverItem = document.createElement('div');
      serverItem.className = 'server-item';
      
      const statusClass = server.status === 'online' ? 'online' : 'offline';
      const statusIcon = server.status === 'online' ? 'fa-check-circle' : 'fa-times-circle';
      const statusText = server.status === 'online' ? '온라인' : '오프라인';
      
      const roleText = server.role === 'central' ? '중앙 서버' : '클라이언트';
      const roleClass = server.role === 'central' ? 'role-central' : 'role-client';
      
      serverItem.innerHTML = `
        <div class="server-info">
          <div class="server-name">${server.label || server.id}</div>
          <div class="server-details">
            <span><i class="fas fa-server"></i> ${server.id}</span>
            <span class="server-role ${roleClass}">
              <i class="fas ${server.role === 'central' ? 'fa-crown' : 'fa-desktop'}"></i>
              ${roleText}
            </span>
            <span class="server-status ${statusClass}">
              <i class="fas ${statusIcon}"></i>
              ${statusText}
            </span>
          </div>
        </div>
        <div class="server-actions">
          ${server.id !== 'main' ? `
          <button class="btn-server-action test" onclick="testServerConnectionById('${server.id}')" title="연결">
            <i class="fas fa-plug"></i>
            <span>연결</span>
          </button>
          <button class="btn-server-action edit" onclick="editServer('${server.id}')" title="수정">
            <i class="fas fa-edit"></i>
            <span>수정</span>
          </button>
          <button class="btn-server-action delete" onclick="deleteServer('${server.id}')" title="삭제">
            <i class="fas fa-trash"></i>
            <span>삭제</span>
          </button>
          ` : ''}
        </div>
      `;
      
      serverList.appendChild(serverItem);
    });
    
    // 서버 그래프 뷰가 활성화되어 있으면 그래프도 업데이트
    if (document.getElementById('serverGraphView') && document.getElementById('serverGraphView').style.display !== 'none') {
      renderServerGraph(servers);
    }
  } catch (error) {
    console.error('서버 목록 로드 오류:', error);
    const errorMessage = error.message || '서버 목록을 불러오는 중 오류가 발생했습니다.';
    showToast(errorMessage, 'error');
    
    // 에러 발생 시에도 currentServers를 빈 배열로 초기화하여 UI 일관성 유지
    currentServers = [];
    
    // 에러 상태 표시
    const serverList = document.getElementById('serverList');
    if (serverList) {
      serverList.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-exclamation-triangle" style="color: #ef4444; font-size: 2rem; margin-bottom: 1rem;"></i>
          <p style="color: #ef4444;">${errorMessage}</p>
          <button class="btn-modern btn-primary" onclick="loadServerList()" style="margin-top: 1rem;">
            <i class="fas fa-redo"></i>
            <span>다시 시도</span>
          </button>
        </div>
      `;
    }
    
    // 서버 그래프 뷰가 활성화되어 있으면 빈 상태 표시
    const serverGraphView = document.getElementById('serverGraphView');
    if (serverGraphView && serverGraphView.style.display !== 'none') {
      renderServerGraph([]);
    }
  }
}

// 서버 추가 폼 모달 열기
function showAddServerForm() {
  const modal = document.getElementById('serverFormModal');
  const formTitle = document.getElementById('serverFormTitle');
  formTitle.innerHTML = '<i class="fas fa-server"></i> 서버 추가';
  document.getElementById('serverForm').reset();
  currentEditingServerId = null;
  document.getElementById('serverTestResult').style.display = 'none';
  modal.style.display = 'flex';
}

// 서버 추가 폼 모달 닫기
function closeServerFormModal() {
  const modal = document.getElementById('serverFormModal');
  modal.style.display = 'none';
  document.getElementById('serverForm').reset();
  currentEditingServerId = null;
  document.getElementById('serverTestResult').style.display = 'none';
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', function(event) {
  const modal = document.getElementById('serverFormModal');
  if (event.target === modal) {
    closeServerFormModal();
  }
});

// 서버 수정
async function editServer(serverId) {
  try {
    const response = await fetch(`/api/nodes/${serverId}`);
    if (!response.ok) {
      throw new Error('서버를 찾을 수 없습니다');
    }
    
    const server = await response.json();
    
    // 서버 정보를 폼에 채우기
    document.getElementById('serverId').value = server.id;
    document.getElementById('serverLabel').value = server.label;
    document.getElementById('serverUrl').value = server.base_url;
    document.getElementById('serverTls').checked = server.tls || false;
    
    // 모달 열기
    const modal = document.getElementById('serverFormModal');
    const formTitle = document.getElementById('serverFormTitle');
    formTitle.innerHTML = '<i class="fas fa-server"></i> 서버 수정';
    currentEditingServerId = serverId;
    document.getElementById('serverTestResult').style.display = 'none';
    modal.style.display = 'flex';
  } catch (error) {
    console.error('서버 수정 오류:', error);
    showToast('서버 정보를 불러오는 중 오류가 발생했습니다.', 'error');
  }
}

// 서버 저장
async function saveServer(event) {
  event.preventDefault();
  
  const formData = {
    id: document.getElementById('serverId').value.trim(),
    label: document.getElementById('serverLabel').value.trim(),
    base_url: document.getElementById('serverUrl').value.trim(),
    tls: document.getElementById('serverTls').checked
  };
  
  if (!formData.id || !formData.label || !formData.base_url) {
    showToast('모든 필수 항목을 입력해주세요.', 'error');
    return;
  }
  
  try {
    let response;
    if (currentEditingServerId) {
      // 수정
      response = await fetch(`/api/nodes/${currentEditingServerId}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
      });
    } else {
      // 추가
      response = await fetch('/api/nodes', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
      });
    }
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '서버 저장 실패');
    }
    
    const result = await response.json();
    showToast(result.message || '서버가 저장되었습니다.', 'success');
    
    // 서버 목록 새로고침
    await loadServerList();
    
    // 노드 선택 드롭다운 업데이트
    await updateNodeSelect();
    
    // 모달 닫기
    closeServerFormModal();
  } catch (error) {
    console.error('서버 저장 오류:', error);
    showToast(error.message || '서버 저장 중 오류가 발생했습니다.', 'error');
  }
}

// 서버 삭제
async function deleteServer(serverId) {
  if (serverId === 'main') {
    showToast('중앙 서버는 삭제할 수 없습니다.', 'error');
    return;
  }
  
  if (!confirm('정말 이 서버를 삭제하시겠습니까?')) {
    return;
  }
  
  // 삭제 전에 해당 서버 아이템 찾기 (더 확실한 방법)
  const serverList = document.getElementById('serverList');
  let serverItemToRemove = null;
  if (serverList) {
    const items = serverList.querySelectorAll('.server-item');
    items.forEach(item => {
      // 서버 ID로 직접 찾기 (더 확실한 방법)
      const serverDetails = item.querySelector('.server-details');
      if (serverDetails) {
        // 첫 번째 span에 서버 ID가 있음: <span><i class="fas fa-server"></i> ${server.id}</span>
        const serverIdSpan = serverDetails.querySelector('span');
        if (serverIdSpan) {
          // 아이콘을 제외한 텍스트만 확인
          const textContent = serverIdSpan.textContent.trim();
          // 서버 ID가 정확히 일치하는지 확인 (공백 제거 후 비교)
          if (textContent === serverId || textContent.includes(serverId)) {
            serverItemToRemove = item;
          }
        }
      }
      // 백업: onclick 속성으로 찾기
      if (!serverItemToRemove) {
        const deleteBtn = item.querySelector(`button[onclick*="deleteServer('${serverId}')"]`);
        if (deleteBtn) {
          serverItemToRemove = item;
        }
      }
    });
  }
  
  try {
    console.log('서버 삭제 요청 시작:', serverId);
    
    const response = await fetch(`/api/nodes/${serverId}`, {
      method: 'DELETE'
    });
    
    console.log('서버 삭제 응답 상태:', response.status, response.statusText);
    
    if (!response.ok) {
      // 에러 응답 처리 개선
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
        console.error('서버 삭제 API 오류:', error);
      } catch (jsonError) {
        // JSON 파싱 실패 시 텍스트로 시도
        try {
          const text = await response.text();
          if (text) {
            errorMessage = text;
          }
          console.error('서버 삭제 응답 (텍스트):', text);
        } catch (textError) {
          console.error('응답 본문 읽기 실패:', textError);
        }
      }
      throw new Error(errorMessage);
    }
    
    // 성공 응답 처리
    let result;
    try {
      result = await response.json();
      console.log('서버 삭제 성공:', result);
    } catch (jsonError) {
      // JSON 파싱 실패 시에도 성공으로 처리 (상태 코드가 200-299)
      console.warn('응답 JSON 파싱 실패, 상태 코드로 성공 판단:', jsonError);
      result = { ok: true, message: '서버가 삭제되었습니다.' };
    }
    
    // 즉시 DOM에서 제거 (목록 새로고침 전에 제거하여 깜빡임 방지)
    if (serverItemToRemove) {
      serverItemToRemove.remove(); // 즉시 제거
    }
    
    showToast(result.message || '서버가 삭제되었습니다.', 'success');
    
    // 서버 목록 새로고침 (재시도 로직 추가)
    let retryCount = 0;
    const maxRetries = 3;
    let loadSuccess = false;
    
    while (retryCount < maxRetries && !loadSuccess) {
      try {
        await loadServerList();
        loadSuccess = true;
        console.log('서버 목록 새로고침 성공');
      } catch (loadError) {
        retryCount++;
        console.error(`서버 목록 새로고침 실패 (시도 ${retryCount}/${maxRetries}):`, loadError);
        
        if (retryCount < maxRetries) {
          // 재시도 전 대기
          await new Promise(resolve => setTimeout(resolve, 500));
        } else {
          // 최종 실패 시 사용자에게 알림
          showToast('서버 목록을 새로고침하지 못했습니다. 페이지를 새로고침해주세요.', 'error');
          console.error('서버 목록 새로고침 최종 실패:', loadError);
        }
      }
    }
    
    // 서버 그래프가 활성화되어 있으면 다시 렌더링
    const serverGraphView = document.getElementById('serverGraphView');
    if (serverGraphView && serverGraphView.style.display !== 'none') {
      setTimeout(() => {
        // currentServers는 loadServerList()에서 이미 업데이트됨
        // 빈 배열이어도 renderServerGraph가 빈 상태를 처리함
        renderServerGraph(currentServers);
      }, 100);
    }
    
    // 노드 선택 드롭다운 업데이트
    try {
      await updateNodeSelect();
    } catch (updateError) {
      console.error('노드 선택 드롭다운 업데이트 실패:', updateError);
    }
    
    // 현재 선택된 노드가 삭제된 경우 기본 노드로 변경
    const nodeSelect = document.getElementById('nodeSelect');
    if (nodeSelect && nodeSelect.value === serverId) {
      nodeSelect.value = 'main';
      try {
        await reloadContainers();
      } catch (reloadError) {
        console.error('컨테이너 새로고침 실패:', reloadError);
      }
    }
  } catch (error) {
    // 네트워크 오류와 기타 오류 구분
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.error('네트워크 오류:', error);
      showToast('서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.', 'error');
    } else if (error.name === 'AbortError') {
      console.error('요청 취소됨:', error);
      showToast('요청이 취소되었습니다.', 'error');
    } else {
      console.error('서버 삭제 오류:', error);
      console.error('오류 상세:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      showToast(error.message || '서버 삭제 중 오류가 발생했습니다.', 'error');
    }
    
    // 에러 발생 시 제거 취소 (이미 제거되지 않았으므로 복구 불필요)
    // 하지만 혹시 모를 경우를 대비해 목록 새로고침 시도
    try {
      await loadServerList();
    } catch (loadError) {
      console.error('에러 후 목록 새로고침 실패:', loadError);
    }
  }
}

// 서버 연결 테스트 (폼에서)
async function testServerConnection() {
  const serverUrl = document.getElementById('serverUrl').value.trim();
  const serverId = document.getElementById('serverId').value.trim();
  
  if (!serverUrl) {
    showToast('URL을 입력해주세요.', 'error');
    return;
  }
  
  if (!serverId) {
    showToast('서버 ID를 입력한 후 테스트해주세요.', 'error');
    return;
  }
  
  const testResult = document.getElementById('serverTestResult');
  testResult.style.display = 'block';
  testResult.className = 'test-result';
  testResult.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 연결 테스트 중...';
  
  try {
    // 먼저 서버가 존재하는지 확인하고, 없으면 임시로 추가하여 테스트
    let testServerId = serverId;
    let needCleanup = false;
    
    try {
      await fetch(`/api/nodes/${serverId}`);
    } catch {
      // 서버가 없으면 임시로 추가 (테스트용)
      const tempServer = {
        id: serverId,
        label: '테스트',
        base_url: serverUrl,
        tls: document.getElementById('serverTls').checked
      };
      
      const addResponse = await fetch('/api/nodes', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(tempServer)
      });
      
      if (!addResponse.ok) {
        throw new Error('임시 서버 추가 실패');
      }
      
      needCleanup = true;
    }
    
    // 연결 테스트
    const testResponse = await fetch(`/api/nodes/${testServerId}/test`, {
      method: 'POST'
    });
    const result = await testResponse.json();
    
    // 임시로 추가한 경우 삭제
    if (needCleanup && !currentEditingServerId) {
      try {
        await fetch(`/api/nodes/${serverId}`, { method: 'DELETE' });
      } catch (e) {
        console.warn('임시 서버 삭제 실패:', e);
      }
    }
    
    if (result.ok) {
      testResult.className = 'test-result success';
      testResult.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <strong>연결 성공!</strong><br>
        Docker 버전: ${result.version || 'N/A'}<br>
        API 버전: ${result.api_version || 'N/A'}
      `;
    } else {
      testResult.className = 'test-result error';
      testResult.innerHTML = `
        <i class="fas fa-times-circle"></i>
        <strong>연결 실패</strong><br>
        ${result.error || '알 수 없는 오류'}
      `;
    }
  } catch (error) {
    testResult.className = 'test-result error';
    testResult.innerHTML = `
      <i class="fas fa-times-circle"></i>
      <strong>연결 테스트 실패</strong><br>
      ${error.message}
    `;
  }
}

// 서버 연결 테스트 (목록에서)
async function testServerConnectionById(serverId) {
  try {
    showToast('연결 테스트 중...', 'info');
    
    const response = await fetch(`/api/nodes/${serverId}/test`, {
      method: 'POST'
    });
    
    const result = await response.json();
    
    if (result.ok) {
      showToast(`연결 성공! Docker ${result.version}`, 'success');
    } else {
      showToast(`연결 실패: ${result.error}`, 'error');
    }
    
    // 서버 목록 새로고침
    await loadServerList();
  } catch (error) {
    console.error('연결 테스트 오류:', error);
    showToast('연결 테스트 중 오류가 발생했습니다.', 'error');
  }
}

// 서버 폼 취소
function cancelServerForm() {
  closeServerFormModal();
}

// 노드 선택 드롭다운 업데이트
async function updateNodeSelect() {
  try {
    const response = await fetch('/api/nodes');
    const nodes = await response.json();
    
    const nodeSelect = document.getElementById('nodeSelect');
    const currentValue = nodeSelect.value;
    
    nodeSelect.innerHTML = '';
    nodes.forEach(node => {
      const option = document.createElement('option');
      option.value = node.id;
      option.textContent = `${node.label} (${node.id})`;
      nodeSelect.appendChild(option);
    });
    
    // 현재 선택값 유지 (존재하는 경우)
    if (currentValue && nodes.find(n => n.id === currentValue)) {
      nodeSelect.value = currentValue;
    } else if (nodes.length > 0) {
      nodeSelect.value = nodes[0].id;
    }
  } catch (error) {
    console.error('노드 목록 업데이트 오류:', error);
  }
}

