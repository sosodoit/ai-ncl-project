document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#search-form");
  const input = document.querySelector("#company-input");
  const loading = document.querySelector("#loading");
  const errorMsg = document.querySelector("#error-message");
  const companyTitle = document.querySelector("#company-title");
  const ratingSection = document.querySelector("#rating-section");
  const companyInfoBox = document.querySelector("#company-content");
  const enpInfoBox = document.querySelector("#enterprise-content");
  const financeInfoBox = document.querySelector("#finance-content");

  if (!form || !input) {
    console.error("❗ #search-form or #company-input not found in DOM");
    return;
  }

  const getParam = (key) =>
    new URLSearchParams(window.location.search).get(key);

  function buildStars(star1 = 0, star2 = 0) {
    const full = Math.floor(star1);
    const half = star1 - full >= 0.5 ? 1 : 0;
    const empty = 5 - full - half;
    return (
      "★".repeat(full) +
      (half ? "☆" : "") +
      '<span class="gray">' + "★".repeat(empty) + "</span>" +
      `<span class="score">(${star1} / ${star2})</span>`
    );
  }

  function buildTable(caption, headers, row) {
    if (!row) return `<p>* ${caption}가(이) 존재하지 않습니다.</p>`;
    return `
      <h3>${caption}</h3>
      <table>
        <tr>${headers.map((h) => `<th>${h}</th>`).join("")}</tr>
        <tr>${row.map((v) => `<td>${v ?? "-"}</td>`).join("")}</tr>
      </table>`;
  }

  function buildListBlock(caption, dataObj) {
    if (!dataObj)
      return `<h3>${caption}</h3><p>* 정보가 없습니다.</p>`;
    const items = Object.entries(dataObj)
      .map(([k, v]) => `<li><strong>${k}</strong>: ${v || "-"}</li>`)
      .join("");
    return `<h3>${caption}</h3><ul>${items}</ul>`;
  }

  function buildReports(reports) {
    if (!Array.isArray(reports) || reports.length === 0)
      return `<h3>분석 리포트</h3><p>* 정보가 없습니다.</p>`;
    return (
      "<h3>분석 리포트</h3>" +
      reports
        .map((r) => {
          const content = (r.content || "")
            .replace(/\n\n/g, "<br><br>")
            .replace(/\n/g, "<br>");
          return `<h4 class="report-title">${r.title || "제목 없음"}</h4>
                  <div class="report-content">${content}</div>`;
        })
        .join("")
    );
  }

  async function fetchCompany(company) {
    loading.style.display = "block";
    errorMsg.style.display = "none";
    // 섹션별 초기화
    companyInfoBox.innerHTML = "";
    enpInfoBox.innerHTML = "";
    financeInfoBox.innerHTML = "";
    
    try {
      const res = await fetch(
        `/api/search-company?company=${encodeURIComponent(company)}`
      );
      const json = await res.json();
      loading.style.display = "none";

      if (!json.success) throw new Error(json.error);
      renderResult(json.data);
    } catch (err) {
      loading.style.display = "none";
      errorMsg.textContent = `에러: ${err.message}`;
      errorMsg.style.display = "block";
    }
  }

  function renderResult(data) {
    companyTitle.textContent = `검색한 기업: ${data.corp_name}`;

    // 별점 표시
    if (data.star1 || data.star2) {
      ratingSection.innerHTML = buildStars(data.star1, data.star2);
      ratingSection.style.display = "block";
    } else {
      ratingSection.style.display = "none";
    }

    // 기업 정보 테이블
    if (data.company_info) {
      const ci = data.company_info;
      companyInfoBox.innerHTML = buildTable(
        "기업 정보",
        ["기업코드", "기업명", "대표자", "구분", "주소", "홈페이지", "IR"],
        [
          ci.corp_code ?? "-",
          ci.corp_name ?? "-",
          ci.ceo_name ?? "-",
          ci.corp_cls ?? "-",
          ci.address ?? "-",
          ci.homepage ?? "-",
          ci.ir_url ?? "-"
        ]
      );
    } else {
      companyInfoBox.innerHTML = "<p>* 기업 정보가 없습니다.</p>";
    }

    let html = "";
    // 엔터프라이즈 정보
    if (data.enterprise_info) {
      const {
        welfare,
        company_basic_info,
        rating,
        company_info
      } = data.enterprise_info;
      
      html += "<hr>" + buildListBlock("복지 제도", welfare);
      html += "<hr>" + buildListBlock("기본 정보", company_basic_info);

      // report_info 제외하고 기타 정보 보여주기
      if (company_info) {
        const { intro, ...rest } = company_info;
        const filteredInfo = { intro };  // intro만 보여줄 경우

        html += "<hr>" + buildListBlock("기타 정보", filteredInfo);

        // ✅ 리포트는 별도 출력
        if (company_info.report_info) {
          html += "<hr>" + buildReports(company_info.report_info);
        }
      }

      enpInfoBox.innerHTML = html;
    } else {
      enpInfoBox.innerHTML = "<p>* 상세 정보가 없습니다.</p>";
    }

    // 재무 정보
    if (data.finance_ofs.length || data.finance_cfs.length) {
      let html = "";

      if (data.finance_ofs.length) {
        html += "<h4>재무제표 (별도)</h4>";
        html += `<table>
                  <tr><th>연도</th><th>매출액</th><th>영업이익</th><th>당기순이익</th></tr>
                  ${data.finance_ofs
                    .map(ofs => `<tr>
                        <td>${ofs.year}</td>
                        <td>${ofs.revenue}</td>
                        <td>${ofs.op_profit}</td>
                        <td>${ofs.net_profit}</td>
                      </tr>`).join("")}
                </table>`;
      }

      if (data.finance_cfs.length) {
        html += "<h4>재무제표 (연결)</h4>";
        html += `<table>
                  <tr><th>연도</th><th>매출액</th><th>영업이익</th><th>당기순이익</th></tr>
                  ${data.finance_cfs
                    .map(cfs => `<tr>
                        <td>${cfs.year}</td>
                        <td>${cfs.revenue}</td>
                        <td>${cfs.op_profit}</td>
                        <td>${cfs.net_profit}</td>
                      </tr>`).join("")}
                </table>`;
      }

      financeInfoBox.innerHTML = html;
    } else {
      financeInfoBox.innerHTML = "<p>* 재무 정보가 없습니다.</p>";
    }
  }

  // 초기화: URL에 ?company= 있으면 자동 조회
  const qs = getParam("company");
  if (qs) {
    input.value = qs;
    fetchCompany(qs);
    history.replaceState(
      {},
      "",
      `/search-company?company=${encodeURIComponent(qs)}`
    );
  }

  // 폼 제출 이벤트
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = input.value.trim();
    if (!name) return;
    history.pushState(
      {},
      "",
      `/search-company?company=${encodeURIComponent(name)}`
    );
    fetchCompany(name);
  });
});
