import { useEffect, useMemo, useRef, useState } from "react";
import { useCart } from "../context/CartContext";
import { apiGetPerfumes } from "../api/api";
import PerfumeCard, { getEmoji } from "../components/PerfumeCard";

const API_URL = "http://localhost:8000";
const formatCOP = (value) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);

const LOCAL_IMAGE_MAP = {
  "dior|sauvage": ["/sauvage/savage.webp", "/sauvage/caja.webp", "/sauvage/eau.webp"],
  "chanel|chanel no. 5": ["/chanel/chanel.webp"],
  "ysl|black opium": ["/blackopium/img1.webp", "/blackopium/img2.webp", "/blackopium/img3.webp"],
  "armani|acqua di gio": ["/acqua-di-gio/img1.webp", "/acqua-di-gio/img2.webp", "/acqua-di-gio/img3.webp"],
  "lancome|la vie est belle": ["/la-vie-est-belle/la-vie-est-belle.webp", "/la-vie-est-belle/la-vie-est-belle.jpg"],
  "chanel|bleu de chanel": ["/bleu-de-chanel/bleu-de-chanel.webp", "/bleu-de-chanel/bleu-de-chanel.jpg"],
};

const normalizeKey = (value = "") =>
  String(value)
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();

const localImagesForPerfume = (p) => {
  const key = `${normalizeKey(p.marca)}|${normalizeKey(p.nombre)}`;
  return LOCAL_IMAGE_MAP[key] || [];
};

const resolveImageSrc = (src) => {
  if (!src || typeof src !== "string") return "";
  const normalized = src.replace(/\\/g, "/").trim();
  if (
    normalized.startsWith("http://") ||
    normalized.startsWith("https://") ||
    normalized.startsWith("data:") ||
    normalized.startsWith("blob:")
  ) {
    return normalized;
  }
  if (normalized.startsWith("/uploads/")) return `${API_URL}${normalized}`;
  if (normalized.startsWith("uploads/")) return `${API_URL}/${normalized}`;
  if (normalized.startsWith("/")) return normalized;
  return `/${normalized}`;
};

export default function CatalogoPage({ push }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState("");
  const [selectedPerfume, setSelectedPerfume] = useState(null);
  const [activeImage, setActiveImage] = useState(0);
  const destacadosRef = useRef(null);
  const { addItem } = useCart();

  const normalizePerfume = (p) => {
    const localFallback = localImagesForPerfume(p);
    const gallery = Array.isArray(p.imagenes)
      ? p.imagenes.filter(Boolean)
      : [p.imagen, p.image, p.imageUrl, p.image_url, p.foto, p.imagen_local, p.imagenLocal].filter(Boolean);
    const images = (gallery.length ? gallery : localFallback)
      .map(resolveImageSrc)
      .filter(Boolean);

    return {
      ...p,
      imagen: images[0] || "",
      imagenes: images,
      descripcion:
        p.descripcion ||
        p.description ||
        "Fragancia sofisticada con excelente fijacion y estela equilibrada para uso diario o especial.",
      categoria: p.categoria || p.familia_olfativa || "Eau de Parfum",
      genero: p.genero || "Unisex",
      tamano: p.tamano || p.tamaño || "100 ml",
    };
  };

  useEffect(() => {
    apiGetPerfumes()
      .then((data) => {
        const source = Array.isArray(data) ? data : [];
        setItems(source.map(normalizePerfume));
      })
      .catch(() => {
        // Datos demo si la API no esta disponible
        setItems([
          {
            id: 1,
            nombre: "Sauvage",
            marca: "Dior",
            precio: 120,
            stock: 15,
            categoria: "Eau de Toilette",
            genero: "Masculino",
            descripcion: "Aroma fresco, especiado y ambarado, ideal para uso nocturno.",
          },
          {
            id: 2,
            nombre: "Chanel No. 5",
            marca: "Chanel",
            precio: 150,
            stock: 8,
            categoria: "Parfum",
            genero: "Femenino",
            descripcion: "Clasico floral-aldehidico elegante y atemporal.",
          },
          { id: 3, nombre: "Black Opium", marca: "YSL", precio: 110, stock: 20 },
          { id: 4, nombre: "Acqua di Gio", marca: "Armani", precio: 95, stock: 12 },
          { id: 5, nombre: "La Vie Est Belle", marca: "Lancome", precio: 105, stock: 5 },
          { id: 6, nombre: "Bleu de Chanel", marca: "Chanel", precio: 145, stock: 0 },
        ].map(normalizePerfume));
        push("Mostrando datos demo — inicia el backend");
      })
      .finally(() => setLoading(false));
  }, []);

  const filtrado = useMemo(() => items.filter((p) =>
    p.nombre?.toLowerCase().includes(busqueda.toLowerCase()) ||
    p.marca?.toLowerCase().includes(busqueda.toLowerCase()) ||
    p.categoria?.toLowerCase().includes(busqueda.toLowerCase())
  ), [items, busqueda]);

  const destacados = useMemo(() => filtrado.slice(0, 10), [filtrado]);

  const openDetails = (perfume) => {
    setSelectedPerfume(perfume);
    setActiveImage(0);
  };

  const moveFeatured = (direction) => {
    if (!destacadosRef.current) return;
    destacadosRef.current.scrollBy({
      left: direction * 320,
      behavior: "smooth",
    });
  };

  const detailImages = selectedPerfume?.imagenes || [];
  const add = (p) => { addItem(p); push(`${p.nombre} agregado al carrito`); };
  const addAndClose = (p) => {
    add(p);
    setSelectedPerfume(null);
  };

  const nextImage = () => setActiveImage((n) =>
    detailImages.length > 0 ? (n + 1) % detailImages.length : 0
  );
  const prevImage = () => setActiveImage((n) =>
    detailImages.length > 0 ? (n - 1 + detailImages.length) % detailImages.length : 0
  );

  const s = {
    page: { padding: "0 40px 64px", minHeight: "90vh" },
    hero: {
      textAlign: "center", padding: "52px 20px 44px",
      background: "linear-gradient(180deg,rgba(201,168,76,.05) 0%,transparent 100%)",
      borderBottom: "1px solid #2E2820", margin: "0 -36px 36px",
    },
    h1: { fontFamily: "'Playfair Display', serif", fontSize: 42, color: "#E8D5A3", lineHeight: 1.1 },
    em: { fontStyle: "italic", color: "#C9A84C" },
    sub: { fontSize: 14, color: "#7A6E64", marginTop: 10 },
    searchBar: {
      display: "flex", alignItems: "center", gap: 10,
      background: "#1E1914", border: "1px solid #3D3428",
      borderRadius: 12, padding: "10px 16px", marginBottom: 36,
    },
    searchInput: {
      background: "none", border: "none", outline: "none",
      color: "#E8E0D5", fontSize: 14, flex: 1,
      fontFamily: "'Jost', sans-serif",
    },
    grid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(285px, 1fr))",
      gap: 30,
      alignItems: "stretch",
    },
    sectionTitle: {
      fontFamily: "'Playfair Display', serif",
      fontSize: 28,
      color: "#E8D5A3",
      margin: "8px 0 18px",
    },
    featuredWrap: { position: "relative", marginBottom: 44 },
    featuredScroller: {
      display: "grid",
      gridAutoFlow: "column",
      gridAutoColumns: "minmax(300px, 340px)",
      gap: 24,
      overflowX: "auto",
      paddingBottom: 12,
      scrollSnapType: "x mandatory",
      scrollbarWidth: "thin",
    },
    featuredCard: {
      scrollSnapAlign: "start",
      border: "1px solid #2E2820",
      borderRadius: 14,
      overflow: "hidden",
      background: "#1A1512",
      cursor: "pointer",
    },
    featuredNav: {
      position: "absolute",
      top: "45%",
      transform: "translateY(-50%)",
      width: 34,
      height: 34,
      borderRadius: "50%",
      border: "1px solid #3D3428",
      background: "rgba(14,11,8,.9)",
      color: "#C9A84C",
      cursor: "pointer",
      zIndex: 2,
    },
    overlay: {
      position: "fixed",
      inset: 0,
      background: "rgba(0,0,0,.6)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: 20,
      zIndex: 999,
    },
    modal: {
      width: "min(980px, 100%)",
      maxHeight: "90vh",
      overflowY: "auto",
      background: "#15110E",
      border: "1px solid #3D3428",
      borderRadius: 16,
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 18,
      padding: 18,
    },
    modalImage: {
      width: "100%",
      height: 420,
      objectFit: "cover",
      borderRadius: 12,
      border: "1px solid #2E2820",
    },
    thumbs: { display: "flex", gap: 10, overflowX: "auto", paddingTop: 10 },
    thumb: {
      width: 62,
      height: 62,
      borderRadius: 8,
      border: "1px solid #3D3428",
      objectFit: "cover",
      cursor: "pointer",
    },
    spinner: {
      width: 30, height: 30, borderRadius: "50%",
      border: "2px solid #2E2820", borderTopColor: "#C9A84C",
      animation: "spin .7s linear infinite",
      margin: "80px auto",
    },
    empty: { textAlign: "center", padding: "60px 20px", color: "#5A504A", fontSize: 14 },
  };

  if (loading) return (
    <div style={s.page}>
      <style>{"@keyframes spin{to{transform:rotate(360deg)}}"}</style>
      <div style={s.spinner}/>
    </div>
  );

  return (
    <div style={s.page}>
      <style>{"@keyframes spin{to{transform:rotate(360deg)}}"}</style>
      <div style={s.hero}>
        <h1 style={s.h1}>Nuestra <em style={s.em}>colección</em></h1>
        <p style={s.sub}>Fragancias exclusivas seleccionadas para ti.</p>
      </div>

      <div style={s.searchBar}>
        <span style={{ color: "#5A504A" }}>🔍</span>
        <input style={s.searchInput}
          placeholder="Buscar por nombre o marca…"
          value={busqueda}
          onChange={e => setBusqueda(e.target.value)}/>
      </div>

      <h2 style={s.sectionTitle}>Destacados</h2>
      <div style={s.featuredWrap}>
        <button style={{ ...s.featuredNav, left: -10 }} onClick={() => moveFeatured(-1)}>‹</button>
        <div style={s.featuredScroller} ref={destacadosRef}>
          {destacados.map((p) => (
            <article key={`destacado-${p.id}`} style={s.featuredCard} onClick={() => openDetails(p)}>
              {p.imagen ? (
                <img src={p.imagen} alt={p.nombre} style={{ width: "100%", height: 200, objectFit: "cover" }} />
              ) : (
                <div style={{ height: 200, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 46 }}>
                  {getEmoji(p.id)}
                </div>
              )}
              <div style={{ padding: 14 }}>
                <div style={{ color: "#C9A84C", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase" }}>{p.marca}</div>
                <div style={{ fontFamily: "'Playfair Display', serif", color: "#E8E0D5", fontSize: 20 }}>{p.nombre}</div>
                <div style={{ color: "#9A8E84", fontSize: 12, marginTop: 4 }}>{p.categoria}</div>
              </div>
            </article>
          ))}
        </div>
        <button style={{ ...s.featuredNav, right: -10 }} onClick={() => moveFeatured(1)}>›</button>
      </div>

      <h2 style={s.sectionTitle}>Todos los perfumes</h2>
      {filtrado.length === 0
        ? <div style={s.empty}>No se encontraron perfumes.</div>
        : <div style={s.grid}>
            {filtrado.map((p) => (
              <PerfumeCard
                key={p.id}
                perfume={p}
                onAdd={add}
                onSelect={openDetails}
              />
            ))}
          </div>
      }

      {selectedPerfume && (
        <div style={s.overlay} onClick={() => setSelectedPerfume(null)}>
          <div style={s.modal} onClick={(e) => e.stopPropagation()}>
            <div>
              <div style={{ position: "relative" }}>
                {detailImages[activeImage] ? (
                  <img src={detailImages[activeImage]} alt={selectedPerfume.nombre} style={s.modalImage} />
                ) : (
                  <div style={{ ...s.modalImage, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 80 }}>
                    {getEmoji(selectedPerfume.id)}
                  </div>
                )}
                {detailImages.length > 1 && (
                  <>
                    <button style={{ ...s.featuredNav, left: 10 }} onClick={prevImage}>‹</button>
                    <button style={{ ...s.featuredNav, right: 10 }} onClick={nextImage}>›</button>
                  </>
                )}
              </div>
              {detailImages.length > 1 && (
                <div style={s.thumbs}>
                  {detailImages.map((src, i) => (
                    <img
                      key={`${src}-${i}`}
                      src={src}
                      alt={`${selectedPerfume.nombre} ${i + 1}`}
                      style={{ ...s.thumb, borderColor: i === activeImage ? "#C9A84C" : "#3D3428" }}
                      onClick={() => setActiveImage(i)}
                    />
                  ))}
                </div>
              )}
            </div>
            <div style={{ paddingTop: 4 }}>
              <div style={{ color: "#C9A84C", letterSpacing: ".1em", textTransform: "uppercase", fontSize: 11 }}>
                {selectedPerfume.marca}
              </div>
              <h3 style={{ fontSize: 34, lineHeight: 1.1, color: "#E8D5A3", margin: "6px 0 10px" }}>
                {selectedPerfume.nombre}
              </h3>
              <p style={{ color: "#9A8E84", lineHeight: 1.65, marginBottom: 16 }}>
                {selectedPerfume.descripcion}
              </p>
              <div style={{ display: "grid", gap: 8, fontSize: 14, color: "#E8E0D5", marginBottom: 18 }}>
                <div><strong style={{ color: "#C9A84C" }}>Categoria:</strong> {selectedPerfume.categoria}</div>
                <div><strong style={{ color: "#C9A84C" }}>Genero:</strong> {selectedPerfume.genero}</div>
                <div><strong style={{ color: "#C9A84C" }}>Tamano:</strong> {selectedPerfume.tamano}</div>
                <div><strong style={{ color: "#C9A84C" }}>Stock:</strong> {selectedPerfume.stock} unidades</div>
              </div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 34, color: "#E8D5A3" }}>
                  {formatCOP(selectedPerfume.precio)}
                </span>
                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    onClick={() => setSelectedPerfume(null)}
                    style={{ background: "transparent", color: "#C9A84C", border: "1px solid #3D3428", borderRadius: 8, padding: "10px 14px", cursor: "pointer" }}
                  >
                    Cerrar
                  </button>
                  <button
                    disabled={selectedPerfume.stock === 0}
                    onClick={() => addAndClose(selectedPerfume)}
                    style={{
                      background: selectedPerfume.stock === 0 ? "transparent" : "#C9A84C",
                      color: selectedPerfume.stock === 0 ? "#5A504A" : "#1A1410",
                      border: selectedPerfume.stock === 0 ? "1px solid #3D3428" : "none",
                      borderRadius: 8,
                      padding: "10px 14px",
                      cursor: selectedPerfume.stock === 0 ? "not-allowed" : "pointer",
                      fontWeight: 600,
                    }}
                  >
                    {selectedPerfume.stock === 0 ? "Sin stock" : "Agregar al carrito"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
