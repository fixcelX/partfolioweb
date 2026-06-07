/* ==========================================================================
   ZAMON MARKET — storefront interactivity (vanilla JS, no dependencies)
   ========================================================================== */
(function () {
  "use strict";

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const I18N = window.ZM_I18N || {};
  const URLS = window.ZM_URLS || {};

  /* ---- Rasm zaxira (tashqi rasm yuklanmasa — chiroyli placeholder) -- */
  // Tashqi (Unsplash) rasmlar ba'zan yuklanmaydi; "buzilgan rasm" belgisi
  // o'rniga brendlangan neytral pleysholder ko'rsatamiz. error hodisasi
  // ko'tarilmagani uchun capture fazasida tinglaymiz.
  const IMG_FALLBACK =
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 200 200'%3E%3Crect width='200' height='200' fill='%23f6efe6'/%3E%3Cg fill='none' stroke='%23c9b89c' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M70 122l85-85a8 8 0 0 1 11 0l9 9a8 8 0 0 1 0 11l-85 85a8 8 0 0 1-11 0l-9-9a8 8 0 0 1 0-11z' transform='translate(-18 -10)'/%3E%3Cpath d='M64 84h72v52a8 8 0 0 1-8 8H72a8 8 0 0 1-8-8z'/%3E%3Cpath d='M64 100l18 14 16-12 38 28'/%3E%3Ccircle cx='86' cy='100' r='6'/%3E%3C/g%3E%3C/svg%3E";
  document.addEventListener(
    "error",
    function (e) {
      const t = e.target;
      if (t && t.tagName === "IMG" && t.src !== IMG_FALLBACK && !t.dataset.fb) {
        t.dataset.fb = "1";
        t.src = IMG_FALLBACK;
      }
    },
    true
  );

  /* ---- CSRF -------------------------------------------------------- */
  function getCookie(name) {
    const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return m ? decodeURIComponent(m.pop()) : "";
  }
  function csrf() {
    const meta = $('meta[name="csrf-token"]');
    return (meta && meta.content) || getCookie("csrftoken");
  }
  async function post(url, data) {
    const body = new URLSearchParams(data);
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrf(),
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      credentials: "same-origin",
      body,
    });
    return { status: res.status, data: await res.json().catch(() => ({})) };
  }

  /* ---- Toast ------------------------------------------------------- */
  function toast(msg, type) {
    let wrap = $(".toast-wrap");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.className = "toast-wrap";
      document.body.appendChild(wrap);
    }
    const el = document.createElement("div");
    el.className = "toast" + (type ? " toast--" + type : "");
    el.textContent = msg;
    wrap.appendChild(el);
    setTimeout(() => {
      el.classList.add("out");
      setTimeout(() => el.remove(), 320);
    }, 2400);
  }
  window.zmToast = toast;

  /* ---- Server xabarlari (Django messages) -> o'ng tomondagi toast --- */
  // Muvaffaqiyat ("Saqlandi" kabi) xabarlari o'ngdan chiqadigan toast bo'ladi.
  // Xato xabarlar sahifada inline qoladi (foydalanuvchi o'qib ulgursin).
  (function initServerMessages() {
    $$(".messages .alert--success").forEach((el) => {
      toast(el.textContent.trim(), "success");
      el.remove();
    });
    $$(".messages").forEach((m) => { if (!m.children.length) m.remove(); });
  })();

  /* ---- Theme ------------------------------------------------------- */
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("zm-theme", t); } catch (e) {}
    $$(".js-theme").forEach((b) => b.setAttribute("aria-pressed", t === "dark"));
  }
  (function initTheme() {
    let t;
    try { t = localStorage.getItem("zm-theme"); } catch (e) {}
    if (!t) t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    applyTheme(t);
  })();

  /* ---- Cart badge / drawer ---------------------------------------- */
  function setBadge(n) {
    $$(".js-cart-count").forEach((el) => {
      el.textContent = n > 0 ? n : "";
      el.dataset.count = n;
    });
  }
  function openDrawer() {
    $(".js-drawer")?.classList.add("is-open");
    $(".js-overlay")?.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }
  function closeDrawer() {
    $(".js-drawer")?.classList.remove("is-open");
    $(".js-overlay")?.classList.remove("is-open");
    document.body.style.overflow = "";
  }
  function renderDrawer(d) {
    if (d.html != null) {
      const body = $(".js-drawer-body");
      if (body) body.innerHTML = d.html;
    }
    if (typeof d.count !== "undefined") setBadge(d.count);
  }

  /* ---- Add to cart ------------------------------------------------- */
  async function addToCart(productId, qty) {
    const r = await post(URLS.cartAdd || "/actions/cart/add/", {
      product_id: productId,
      quantity: qty || 1,
    });
    if (r.status === 200 && r.data.ok) {
      setBadge(r.data.count);
      toast((I18N.added) || "Added to cart", "success");
    } else if (r.status === 404) {
      toast((I18N.error) || "Error", "error");
    } else {
      toast((I18N.error) || "Error", "error");
    }
  }

  /* ---- Wishlist ---------------------------------------------------- */
  async function toggleWish(btn) {
    const id = btn.dataset.product;
    const r = await post(URLS.wishToggle || "/actions/wishlist/toggle/", { product_id: id });
    if (r.status === 401) {
      window.location.href = (r.data.login_url || "/login/") + "?next=" + encodeURIComponent(location.pathname);
      return;
    }
    if (r.data.ok) {
      btn.classList.toggle("is-active", r.data.in_wishlist);
      btn.classList.add("pulse");
      setTimeout(() => btn.classList.remove("pulse"), 420);
      toast(r.data.in_wishlist ? (I18N.wishAdded || "Added") : (I18N.wishRemoved || "Removed"));
      if (!r.data.in_wishlist && btn.dataset.removeOnUnwish === "1") {
        const cell = btn.closest(".js-wish-cell");
        if (cell) {
          cell.classList.add("is-removing");
          setTimeout(() => {
            cell.remove();
            const grid = $(".product-grid");
            if (grid && !grid.children.length) location.reload();
          }, 380);
        }
      }
    }
  }

  /* ---- Global delegated clicks ------------------------------------- */
  document.addEventListener("click", (e) => {
    const t = e.target;

    const themeBtn = t.closest(".js-theme");
    if (themeBtn) {
      applyTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
      return;
    }

    const addBtn = t.closest(".js-add-cart");
    if (addBtn) {
      e.preventDefault();
      if (addBtn.disabled) return;
      const qtyInput = addBtn.dataset.qtyTarget ? $("#" + addBtn.dataset.qtyTarget) : null;
      const qty = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
      addToCart(addBtn.dataset.product, qty);
      return;
    }

    const wishBtn = t.closest(".js-wish");
    if (wishBtn) {
      e.preventDefault();
      toggleWish(wishBtn);
      return;
    }

    // Savat tugmasi alohida sahifaga o'tadi (drawer ishlatilmaydi).
    if (t.closest(".js-drawer-close") || t.closest(".js-overlay")) { closeDrawer(); return; }

    const megaBtn = t.closest(".js-mega-toggle");
    if (megaBtn) {
      e.preventDefault();
      $(".js-mega")?.classList.toggle("is-open");
      return;
    }
    if (!t.closest(".js-mega") && !t.closest(".js-mega-toggle")) {
      $(".js-mega")?.classList.remove("is-open");
    }

    const langBtn = t.closest(".js-lang-toggle");
    if (langBtn) {
      e.preventDefault();
      langBtn.nextElementSibling?.classList.toggle("is-open");
      return;
    } else if (!t.closest(".js-lang-menu")) {
      $(".js-lang-menu")?.classList.remove("is-open");
    }

    // Drawer item qty / remove
    const dInc = t.closest(".js-drawer-inc");
    const dDec = t.closest(".js-drawer-dec");
    const dRem = t.closest(".js-drawer-remove");
    if (dInc || dDec || dRem) {
      const row = t.closest("[data-item]");
      if (!row) return;
      const id = row.dataset.item;
      const cur = parseInt(row.dataset.qty || "1", 10);
      if (dRem) updateCart(id, 0, true);
      else updateCart(id, dInc ? cur + 1 : cur - 1, true);
      return;
    }
  });

  async function refreshDrawer() {
    const r = await fetch(URLS.cartDrawer || "/actions/cart/drawer/", {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin",
    });
    const d = await r.json().catch(() => ({}));
    renderDrawer(d);
  }

  async function updateCart(itemId, qty, inDrawer) {
    const r = await post(URLS.cartUpdate || "/actions/cart/update/", {
      item_id: itemId,
      quantity: qty,
    });
    if (!r.data.ok) return;
    if (inDrawer) renderDrawer(r.data);
    setBadge(r.data.count);

    // Cart page live update (reload'siz)
    const pageRow = $('.cart-item[data-item="' + itemId + '"]');
    if (pageRow) {
      if (r.data.removed) {
        pageRow.style.transition = "opacity .2s, transform .2s";
        pageRow.style.opacity = "0";
        pageRow.style.transform = "translateX(12px)";
        setTimeout(() => {
          pageRow.remove();
          if (!$$(".cart-item").length) location.reload();
        }, 220);
      } else {
        const sub = pageRow.querySelector(".js-item-sub");
        if (sub && r.data.item_subtotal_fmt) sub.textContent = r.data.item_subtotal_fmt;
        const q = pageRow.querySelector(".js-item-qty");
        const newQty = typeof r.data.item_qty !== "undefined" ? r.data.item_qty : qty;
        if (q) q.textContent = newQty;
        pageRow.dataset.qty = newQty;
      }
      updateCartSummary(r.data.total_fmt);
    }
  }
  function updateCartSummary(totalFmt) {
    if (!totalFmt) return;
    $$(".js-cart-total").forEach((el) => (el.textContent = totalFmt));
  }

  /* ---- Cart page qty buttons -------------------------------------- */
  document.addEventListener("click", (e) => {
    const inc = e.target.closest(".js-page-inc");
    const dec = e.target.closest(".js-page-dec");
    const rem = e.target.closest(".js-page-remove");
    if (!inc && !dec && !rem) return;
    const row = e.target.closest(".cart-item");
    if (!row) return;
    const id = row.dataset.item;
    const cur = parseInt(row.dataset.qty || "1", 10);
    if (rem) updateCart(id, 0, false);
    else updateCart(id, inc ? cur + 1 : cur - 1, false);
  });

  /* ---- Product detail: gallery + stepper -------------------------- */
  function initGallery() {
    const main = $(".js-gallery-main");
    if (!main) return;
    $$(".js-thumb").forEach((thumb) => {
      thumb.addEventListener("click", () => {
        main.src = thumb.dataset.src;
        $$(".js-thumb").forEach((x) => x.classList.remove("is-active"));
        thumb.classList.add("is-active");
      });
    });
  }
  function initStepper() {
    const wrap = $(".js-stepper");
    if (!wrap) return;
    const input = $(".js-qty-input", wrap);
    const max = parseInt(input.max, 10) || 99;
    $(".js-step-dec", wrap)?.addEventListener("click", () => {
      input.value = Math.max(1, (parseInt(input.value, 10) || 1) - 1);
    });
    $(".js-step-inc", wrap)?.addEventListener("click", () => {
      input.value = Math.min(max, (parseInt(input.value, 10) || 1) + 1);
    });
  }

  /* ---- Tabs -------------------------------------------------------- */
  function initTabs() {
    $$(".js-tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = btn.dataset.tab;
        $$(".js-tab").forEach((b) => b.classList.toggle("is-active", b === btn));
        $$(".js-tab-panel").forEach((p) =>
          p.classList.toggle("is-active", p.dataset.panel === target)
        );
      });
    });
  }

  /* ---- Search suggestions ----------------------------------------- */
  function initSearch() {
    const input = $(".js-search-input");
    const box = $(".js-suggest");
    if (!input || !box) return;
    let timer;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      const q = input.value.trim();
      if (q.length < 2) { box.classList.remove("is-open"); return; }
      timer = setTimeout(async () => {
        const r = await fetch((URLS.searchSuggest || "/actions/search/") + "?q=" + encodeURIComponent(q), {
          credentials: "same-origin",
        });
        const d = await r.json().catch(() => ({ results: [] }));
        if (!d.results.length) { box.classList.remove("is-open"); return; }
        box.innerHTML = d.results
          .map(
            (p) =>
              '<a class="suggest__item" href="/product/' + encodeURIComponent(p.slug) + '/">' +
              (p.image ? '<img src="' + escapeHtml(p.image) + '" alt="" loading="lazy">' : '<span class="suggest__item-noimg"></span>') +
              '<span class="suggest__name">' + escapeHtml(p.name) + "</span>" +
              '<span class="suggest__price" style="margin-left:auto">' + escapeHtml(p.price) + "</span>" +
              "</a>"
          )
          .join("") +
          '<button class="suggest__footer" type="button" data-q="' + escapeHtml(q) + '">' +
          escapeHtml((I18N.viewAllResults || "View all results")) + ' “' + escapeHtml(q) + '”</button>';
        box.classList.add("is-open");
      }, 220);
    });
    box.addEventListener("click", (e) => {
      const f = e.target.closest(".suggest__footer");
      if (f) window.location.href = "/search/?q=" + encodeURIComponent(f.dataset.q || "");
    });
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".search")) box.classList.remove("is-open");
    });
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );
  }

  /* ---- Header scroll + back to top -------------------------------- */
  function initScroll() {
    const header = $(".header");
    const toTop = $(".js-to-top");
    const onScroll = () => {
      const y = window.scrollY;
      header?.classList.toggle("is-scrolled", y > 8);
      toTop?.classList.toggle("is-visible", y > 600);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    toTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  /* ---- Scroll reveal ---------------------------------------------- */
  function initReveal() {
    const els = $$(".reveal");
    if (!els.length || !("IntersectionObserver" in window)) {
      els.forEach((el) => el.classList.add("in"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
        });
      },
      { rootMargin: "-40px" }
    );
    els.forEach((el) => io.observe(el));
  }

  /* ---- Esc closes overlays ---------------------------------------- */
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeDrawer();
      $(".js-mega")?.classList.remove("is-open");
      $(".js-suggest")?.classList.remove("is-open");
    }
  });

  /* ---- Init -------------------------------------------------------- */
  document.addEventListener("DOMContentLoaded", () => {
    initGallery();
    initStepper();
    initTabs();
    initSearch();
    initScroll();
    initReveal();
  });
})();
