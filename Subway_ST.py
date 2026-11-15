
class Dijkstra:
    def __init__(self, nodes):
        self.nodes = nodes
        self.visits = set()
        self.graph = []
        self.cost = {}
        for node in self.nodes:
            self.cost[node] = [float("inf"),None]

    def setEdge(self, a, b, w):
        self.graph.append((a,b,w))   

    def getPath(self, start, end):
        curNode = start
        self.cost[curNode][0] = 0    

        while True:        
            self.visits.add(curNode)       # 현재 노드를 방문 처리한다.
            self.nodes.remove(curNode)     # 남은 노드집합에서 현재 노드를 삭제한다.
            neighbors = self._neighbor(curNode) # 현재 노드에서 갈 수 있는 이웃노드 집합을 구한다.
            
            # 모든 이웃에 대해 현재 노드를 통해 이웃노드에 접근하는 cost가 더 작을 경우, cost 값을 갱신하고 부모노드를 변경한다.
            for node in neighbors:
                if self.cost[curNode][0] + self._getWeight(curNode,node) < self.cost[node][0]:
                    self.cost[node][0] = self.cost[curNode][0] + self._getWeight(curNode, node)
                    self.cost[node][1] = curNode
                    
            if len(self.nodes) > 0:
                curNode = self._dicFilter() # 이웃노드 중 가장 빠르게 갈 수 있는 노드를 구해 현재 노드를 갱신한다.(Greedy Algorithm)
            else:
                break

        path = [end]

        while end != start:
            path.append(self.cost[end][1])
            end = self.cost[end][1]

        return path[::-1]

    def _neighbor(self, curNode):
        # curNode에 연결된 이웃노드를 리스트로 리턴한다.
        neighbor = {}
        for node in self.graph:
            if node[0] == curNode:
                neighbor[node[1]]= node[2]
            elif node[1] == curNode:
                neighbor[node[0]] = node[2]
        return neighbor

    def _getWeight(self, n1, n2):
        # 그래프에서 노드 n1, n2의 가중값을 리턴한다.
        for node in self.graph:
            if node[0] == n1 and node[1] == n2:
                return node[2]
            elif node[0] == n2 and node[1] == n1:
                return node[2]
        return None

    def _dicFilter(self):
        # 이동할 수 있는 노드 중에 cost기 최소인 노드를 리턴한다.
        # cost 중에 현재 노드에서 이동 가능한 노드만 cost가 갱신 되어 있으므로 최소노드는 이동 가능한 노드 중에만 선택된다.
        import sys
        mini = sys.maxsize
        for key, value in self.cost.items():
            if key in self.nodes: # 아직 방문하지 않은 노드만
                if value[0] < mini:
                    mini = value[0]
                    curNode = key
        return curNode
    
import csv
import folium
import streamlit as st
import streamlit.components.v1 as components

# 1. 데이터 로딩 및 캐싱 (중복 로딩 방지)
@st.cache_resource
def load_subway_data():
    # 지하철 위치 데이터 딕셔너리 구성
    subwayLoc = {}
    with open('subwayLocation.csv', 'r', encoding='utf-8-sig') as f:
        rdr = csv.reader(f)
        for line in rdr:
            if line[0] not in subwayLoc:
                subwayLoc[line[0]] = [float(line[1]), float(line[2])]

    # 지하철역 간 거리 데이터로 노드 집합 생성 및 다익스트라 초기화
    nodes = set()
    with open('subway.csv', 'r', encoding='utf-8-sig') as f:
        rdr = csv.reader(f)
        for line in rdr:
            nodes.add(line[0])
            nodes.add(line[1])

    # Dijkstra 클래스가 정의되어 있다고 가정 (기존 코드와 동일)
    d = Dijkstra(nodes) 
    
    with open('subway.csv', 'r', encoding='utf-8-sig') as f:
        rdr = csv.reader(f)
        for line in rdr:
            d.setEdge(line[0], line[1], int(line[2]))
            
    return subwayLoc, nodes, d

# 데이터 불러오기
try:
    subwayLoc, nodes, d = load_subway_data()
    sorted_nodes = sorted(list(nodes))
except FileNotFoundError:
    st.error("subwayLocation.csv 또는 subway.csv 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    st.stop()

# 2. 웹 UI 구성
st.title("지하철 최단 경로 과제")
st.markdown("출발역과 도착역을 선택하세요.")

# 2열 레이아웃으로 출발역과 도착역 선택창 배치
col1, col2 = st.columns(2)

with col1:
    station_start = st.selectbox("출발역", sorted_nodes, index=0)

with col2:
    station_destination = st.selectbox("도착역", sorted_nodes, index=min(1, len(sorted_nodes)-1))

# 3. 경로 찾기 및 지도 시각화 실행 버튼
if st.button("경로 탐색 및 지도 보기", type="primary"):
    if station_start == station_destination:
        st.warning("출발역과 도착역이 같습니다. 서로 다른 역을 선택해주세요.")
    else:
        # 다익스트라 알고리즘을 통한 경로 탐색
        pathList = d.getPath(station_start, station_destination)
        pathNames = []
        pathLine = []
        xbar = 0
        ybar = 0
        
        for item in pathList:
            station_name = item[:-3]
            pathNames.append(station_name)
            xbar += subwayLoc[station_name][0]
            ybar += subwayLoc[station_name][1]
            pathLine.append(item[-2])

        # 평균 좌표 계산 (지도 중심점 설정용)
        xbar /= len(pathList)
        ybar /= len(pathList)

        # Folium 지도 생성
        map_osm = folium.Map(location=[xbar, ybar], zoom_start=12)
        paths = []
        
        # 지도 위에 CircleMarker 및 PolyLine 추가
        for name in pathNames:
            loc = subwayLoc[name]
            idx = pathNames.index(name)
            line_no = pathLine[idx]
            
            # 노선별 색상 지정
            if line_no == '1': color = 'blue'
            elif line_no == '2': color = 'green'
            elif line_no == '3': color = 'orange'
            elif line_no == '4': color = 'cyan'
            else: color = 'gray'
            
            folium.CircleMarker(
                loc, radius=6, popup=name, 
                color=color, fill=True, fill_color=color
            ).add_to(map_osm)
            paths.append(loc)

        folium.PolyLine(paths, color="red", weight=4, opacity=0.8).add_to(map_osm)

        # 결과 출력
        st.success(f"총 경유 역: {len(pathList)}개")
        
        # Streamlit 내부에 Folium 지도 렌더링
        map_html = map_osm._repr_html_()
        components.html(map_html, height=500, scrolling=False)