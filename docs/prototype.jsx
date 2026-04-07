import { useState, useMemo, useRef, useEffect, useCallback } from "react";

// ─── DATA ─────────────────────────────────────────────────────────────────────

const LENSES = [
  // 7Artisans
  { brand:"7Artisans", model:"7.5mm F2.8",         type:"P", flMin:8,   flMax:8,   ap:2.8,  ois:false, wr:false, lm:false, mtf:6,  kg:0.3, thread:0,   price:150,  est:true, format:"X"  },
  { brand:"7Artisans", model:"25mm f1.8",           type:"P", flMin:25,  flMax:25,  ap:1.8,  ois:false, wr:false, lm:false, mtf:5,  kg:0.2, thread:46,  price:100,  est:true, format:"X"  },
  { brand:"7Artisans", model:"35mm f1.2",           type:"P", flMin:35,  flMax:35,  ap:1.2,  ois:false, wr:false, lm:false, mtf:6,  kg:0.2, thread:43,  price:150,  est:true, format:"X"  },
  { brand:"7Artisans", model:"35mm f2",             type:"P", flMin:35,  flMax:35,  ap:2.0,  ois:false, wr:false, lm:false, mtf:5,  kg:0.3, thread:43,  price:200,  est:true, format:"X"  },
  { brand:"7Artisans", model:"50mm f1.8",           type:"P", flMin:50,  flMax:50,  ap:1.8,  ois:false, wr:false, lm:false, mtf:7,  kg:0.2, thread:52,  price:100,  est:true, format:"X"  },
  { brand:"7Artisans", model:"55mm f1.4",           type:"P", flMin:55,  flMax:55,  ap:1.4,  ois:false, wr:false, lm:false, mtf:7,  kg:0.3, thread:49,  price:100,  est:true, format:"X"  },
  // Carl Zeiss
  { brand:"Carl Zeiss", model:"Touit 12mm f/2.8",  type:"P", flMin:12,  flMax:12,  ap:2.8,  ois:false, wr:false, lm:false, mtf:8,  kg:0.3, thread:67,  price:900,  est:true, format:"X", af:true  },
  { brand:"Carl Zeiss", model:"Touit 32mm f/1.8",  type:"P", flMin:32,  flMax:32,  ap:1.8,  ois:false, wr:false, lm:false, mtf:7,  kg:0.2, thread:52,  price:600,  est:true, format:"X", af:true  },
  { brand:"Carl Zeiss", model:"Touit 50mm f/2.8 Macro", type:"P", flMin:50, flMax:50, ap:2.8, ois:false, wr:false, lm:false, mtf:8, kg:0.3, thread:52, price:850,  est:true, format:"X", af:true  },
  // Fujifilm primes
  { brand:"Fujifilm", model:"xf 14mm f/2.8",       type:"P", flMin:14,  flMax:14,  ap:2.8,  ois:false, wr:false, lm:false, mtf:8,  kg:0.2, thread:58,  price:950,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 16mm f/1.4",       type:"P", flMin:16,  flMax:16,  ap:1.4,  ois:false, wr:true,  lm:false, mtf:8,  kg:0.4, thread:67,  price:1000,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 18mm f/1.4",       type:"P", flMin:18,  flMax:18,  ap:1.4,  ois:false, wr:true,  lm:true,  mtf:9,  kg:0.4, thread:62,  price:1100,  est:false, format:"X", sweetSpot:"f/2.8"  },
  { brand:"Fujifilm", model:"xf 18mm f/2.0",       type:"P", flMin:18,  flMax:18,  ap:2.0,  ois:false, wr:false, lm:false, mtf:7,  kg:0.1, thread:52,  price:550,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 23mm f/1.4",       type:"P", flMin:23,  flMax:23,  ap:1.4,  ois:false, wr:false, lm:false, mtf:8,  kg:0.3, thread:62,  price:950,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 23mm f/2.0",       type:"P", flMin:23,  flMax:23,  ap:2.0,  ois:false, wr:true,  lm:false, mtf:8,  kg:0.2, thread:43,  price:500,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 27mm f/2.8",       type:"P", flMin:27,  flMax:27,  ap:2.8,  ois:false, wr:false, lm:false, mtf:7,  kg:0.1, thread:39,  price:460,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 30mm f/2.8 Macro", type:"P", flMin:30,  flMax:30,  ap:2.8,  ois:false, wr:true,  lm:true,  mtf:7,  kg:0.2, thread:43,  price:700,  est:false, format:"X", sweetSpot:"f/8"  },
  { brand:"Fujifilm", model:"xf 33mm f/1.4 LM WR", type:"P", flMin:33,  flMax:33,  ap:1.4,  ois:false, wr:true,  lm:true,  mtf:9,  kg:0.4, thread:67,  price:850,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 35mm f/1.4",       type:"P", flMin:35,  flMax:35,  ap:1.4,  ois:false, wr:false, lm:false, mtf:7,  kg:0.2, thread:52,  price:600,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 35mm f/2.0",       type:"P", flMin:35,  flMax:35,  ap:2.0,  ois:false, wr:true,  lm:false, mtf:7,  kg:0.2, thread:43,  price:460,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 50mm f/1.0 R WR",  type:"P", flMin:50,  flMax:50,  ap:1.0,  ois:false, wr:true,  lm:false, mtf:8,  kg:0.9, thread:77,  price:1600,  est:false, format:"X", sweetSpot:"f/4"  },
  { brand:"Fujifilm", model:"xf 50mm f/2.0",       type:"P", flMin:50,  flMax:50,  ap:2.0,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.2, thread:62,  price:500,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 56mm f/1.2",       type:"P", flMin:56,  flMax:56,  ap:1.2,  ois:false, wr:false, lm:false, mtf:8,  kg:0.4, thread:62,  price:900,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 60mm f/2.4 Macro", type:"P", flMin:60,  flMax:60,  ap:2.4,  ois:false, wr:false, lm:false, mtf:8,  kg:0.2, thread:39,  price:700,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 80mm f/2.8 Macro", type:"P", flMin:80,  flMax:80,  ap:2.8,  ois:true,  wr:true,  lm:true,  mtf:9,  kg:0.8, thread:62,  price:1350,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 90mm f/2.0",       type:"P", flMin:90,  flMax:90,  ap:2.0,  ois:false, wr:true,  lm:true,  mtf:9,  kg:0.5, thread:62,  price:800,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 200mm f/2.0",      type:"P", flMin:200, flMax:200, ap:2.0,  ois:true,  wr:true,  lm:true,  mtf:10, kg:2.3, thread:105, price:6000,  est:false, format:"X"  },
  // Fujifilm zooms
  { brand:"Fujifilm", model:"xf 8-16mm f/2.8",     type:"Z", flMin:8,   flMax:16,  ap:2.8,  ois:true,  wr:true,  lm:false, mtf:9,  kg:0.8, thread:0,   price:2000,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 10-24mm f/4 R OIS WR",  type:"Z", flMin:10,  flMax:24,  ap:4.0,  ois:true,  wr:true,  lm:false, mtf:8,  kg:0.4, thread:72,  price:1000,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 10-24mm f/4 R OIS",     type:"Z", flMin:10,  flMax:24,  ap:4.0,  ois:true,  wr:false, lm:false, mtf:8,  kg:0.4, thread:72,  price:600,   est:true,  format:"X"  },
  { brand:"Fujifilm", model:"xf 16-55mm f/2.8",    type:"Z", flMin:16,  flMax:55,  ap:2.8,  ois:false, wr:true,  lm:true,  mtf:8,  kg:0.7, thread:77,  price:1200,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 18-55mm f/2.8-4.0",type:"Z", flMin:18,  flMax:55,  ap:2.8,  ois:true,  wr:false, lm:true,  mtf:7,  kg:0.3, thread:58,  price:750,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 18-135mm f/3.5-5.6",type:"Z",flMin:18,  flMax:135, ap:3.5,  ois:true,  wr:true,  lm:true,  mtf:6,  kg:0.5, thread:67,  price:800,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 50-140mm f/2.8",   type:"Z", flMin:50,  flMax:140, ap:2.8,  ois:true,  wr:true,  lm:true,  mtf:8,  kg:1.0, thread:72,  price:1600,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 55-200mm f/3.5-4.8",type:"Z",flMin:55,  flMax:200, ap:3.5,  ois:true,  wr:false, lm:true,  mtf:7,  kg:0.6, thread:62,  price:700,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 100-400mm f/4.5-5.6",type:"Z",flMin:100,flMax:400, ap:4.5,  ois:true,  wr:true,  lm:true,  mtf:8,  kg:1.4, thread:77,  price:1850,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xc 15-45mm f/3.5-5.6",type:"Z", flMin:15,  flMax:45,  ap:3.5,  ois:true,  wr:false, lm:false, mtf:6,  kg:0.1, thread:52,  price:310,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xc 16-50mm f/3.5-5.6",type:"Z", flMin:16,  flMax:50,  ap:3.5,  ois:true,  wr:false, lm:false, mtf:6,  kg:0.2, thread:58,  price:310,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xc 50-230mm f/4.5-6.7",type:"Z",flMin:50,  flMax:230, ap:4.5,  ois:true,  wr:false, lm:false, mtf:6,  kg:0.4, thread:58,  price:410,  est:false, format:"X"  },
  // Handevision
  { brand:"Handevision", model:"IBERIT 24mm f2.4",  type:"P", flMin:24,  flMax:24,  ap:2.4,  ois:false, wr:false, lm:false, mtf:7,  kg:0.5, thread:49,  price:600,  est:true, format:"X"  },
  { brand:"Handevision", model:"IBERIT 35mm f2.4",  type:"P", flMin:35,  flMax:35,  ap:2.4,  ois:false, wr:false, lm:false, mtf:6,  kg:0.3, thread:49,  price:600,  est:true, format:"X"  },
  { brand:"Handevision", model:"IBERIT 50mm f2.4",  type:"P", flMin:50,  flMax:50,  ap:2.4,  ois:false, wr:false, lm:false, mtf:7,  kg:0.3, thread:49,  price:600,  est:true, format:"X"  },
  { brand:"Handevision", model:"IBERIT 75mm f2.4",  type:"P", flMin:75,  flMax:75,  ap:2.4,  ois:false, wr:false, lm:false, mtf:7,  kg:0.3, thread:49,  price:600,  est:true, format:"X"  },
  { brand:"Handevision", model:"IBERIT 90mm f/2.4", type:"P", flMin:90,  flMax:90,  ap:2.4,  ois:false, wr:false, lm:false, mtf:7,  kg:0.4, thread:49,  price:500,  est:true, format:"X"  },
  // Kamlan
  { brand:"Kamlan", model:"28mm f1.4",              type:"P", flMin:28,  flMax:28,  ap:1.4,  ois:false, wr:false, lm:false, mtf:6,  kg:0.4, thread:52,  price:200,  est:true, format:"X"  },
  { brand:"Kamlan", model:"50mm f1.1",              type:"P", flMin:50,  flMax:50,  ap:1.1,  ois:false, wr:false, lm:false, mtf:7,  kg:0.3, thread:52,  price:200,  est:true, format:"X"  },
  // Meike
  { brand:"Meike", model:"6.5mm Fisheye f2.0",      type:"P", flMin:6,   flMax:6,   ap:2.0,  ois:false, wr:false, lm:false, mtf:8,  kg:0.3, thread:0,   price:150,  est:true, format:"X"  },
  { brand:"Meike", model:"8mm Fisheye f3.5",        type:"P", flMin:8,   flMax:8,   ap:3.5,  ois:false, wr:false, lm:false, mtf:7,  kg:0.5, thread:0,   price:200,  est:true, format:"X"  },
  { brand:"Meike", model:"12mm f2.8",               type:"P", flMin:12,  flMax:12,  ap:2.8,  ois:false, wr:false, lm:false, mtf:6,  kg:0.4, thread:72,  price:260,  est:true, format:"X"  },
  { brand:"Meike", model:"25mm f0.95",              type:"P", flMin:25,  flMax:25,  ap:0.95, ois:false, wr:false, lm:false, mtf:7,  kg:0.6, thread:55,  price:600,  est:true, format:"X"  },
  { brand:"Meike", model:"85mm f2.8 Macro",         type:"P", flMin:85,  flMax:85,  ap:2.8,  ois:false, wr:false, lm:false, mtf:8,  kg:0.5, thread:55,  price:310,  est:true, format:"X"  },
  // Meyer Optik
  { brand:"Meyer Optik", model:"Primoplan 58mm f1.9",type:"P",flMin:58,  flMax:58,  ap:1.9,  ois:false, wr:false, lm:false, mtf:8,  kg:0.2, thread:37,  price:1300,  est:true, format:"X"  },
  { brand:"Meyer Optik", model:"Primoplan 75mm f1.9",type:"P",flMin:75,  flMax:75,  ap:1.9,  ois:false, wr:false, lm:false, mtf:8,  kg:0.3, thread:52,  price:2000,  est:true, format:"X"  },
  { brand:"Meyer Optik", model:"Trioplan 50mm f/2.9",type:"P",flMin:50,  flMax:50,  ap:2.9,  ois:false, wr:false, lm:false, mtf:7,  kg:0.2, thread:36,  price:1550,  est:true, format:"X"  },
  { brand:"Meyer Optik", model:"Trioplan 100mm f2.8",type:"P",flMin:100, flMax:100, ap:2.8,  ois:false, wr:false, lm:false, mtf:7,  kg:0.8, thread:52,  price:1650,  est:true, format:"X"  },
  // Samyang
  { brand:"Samyang", model:"8mm f/2.8",             type:"P", flMin:8,   flMax:8,   ap:2.8,  ois:false, wr:false, lm:false, mtf:9,  kg:0.2, thread:0,   price:310,  est:true, format:"X"  },
  { brand:"Samyang", model:"8mm f/3.5",             type:"P", flMin:8,   flMax:8,   ap:3.5,  ois:false, wr:false, lm:false, mtf:7,  kg:0.4, thread:0,   price:330,  est:true, format:"X"  },
  { brand:"Samyang", model:"10mm f/2.8",            type:"P", flMin:10,  flMax:10,  ap:2.8,  ois:false, wr:false, lm:false, mtf:7,  kg:0.6, thread:0,   price:500,  est:true, format:"X"  },
  { brand:"Samyang", model:"12mm f/2",              type:"P", flMin:12,  flMax:12,  ap:2.0,  ois:false, wr:false, lm:false, mtf:8,  kg:0.3, thread:67,  price:410,  est:true, format:"X"  },
  { brand:"Samyang", model:"12mm f/2.8",            type:"P", flMin:12,  flMax:12,  ap:2.8,  ois:false, wr:false, lm:false, mtf:7,  kg:0.5, thread:0,   price:500,  est:true, format:"X"  },
  { brand:"Samyang", model:"14mm f/2.8",            type:"P", flMin:14,  flMax:14,  ap:2.8,  ois:false, wr:false, lm:false, mtf:7,  kg:0.6, thread:0,   price:410,  est:true, format:"X"  },
  { brand:"Samyang", model:"16mm f/2",              type:"P", flMin:16,  flMax:16,  ap:2.0,  ois:false, wr:false, lm:false, mtf:8,  kg:0.6, thread:77,  price:460,  est:true, format:"X"  },
  { brand:"Samyang", model:"20mm f/1.8",            type:"P", flMin:20,  flMax:20,  ap:1.8,  ois:false, wr:false, lm:false, mtf:7,  kg:0.5, thread:77,  price:490,  est:true, format:"X"  },
  { brand:"Samyang", model:"21mm F1.4",             type:"P", flMin:21,  flMax:21,  ap:1.4,  ois:false, wr:false, lm:false, mtf:7,  kg:0.3, thread:58,  price:410,  est:true, format:"X"  },
  { brand:"Samyang", model:"35mm f/1.2",            type:"P", flMin:35,  flMax:35,  ap:1.2,  ois:false, wr:false, lm:false, mtf:7,  kg:0.4, thread:62,  price:410,  est:true, format:"X"  },
  { brand:"Samyang", model:"35mm f/1.4",            type:"P", flMin:35,  flMax:35,  ap:1.4,  ois:false, wr:false, lm:false, mtf:9,  kg:0.7, thread:77,  price:500,  est:true, format:"X"  },
  { brand:"Samyang", model:"50mm f/1.2",            type:"P", flMin:50,  flMax:50,  ap:1.2,  ois:false, wr:false, lm:false, mtf:8,  kg:0.4, thread:62,  price:430,  est:true, format:"X"  },
  { brand:"Samyang", model:"50mm f/1.4",            type:"P", flMin:50,  flMax:50,  ap:1.4,  ois:false, wr:false, lm:false, mtf:7,  kg:0.5, thread:77,  price:410,  est:true, format:"X"  },
  { brand:"Samyang", model:"85mm f/1.4",            type:"P", flMin:85,  flMax:85,  ap:1.4,  ois:false, wr:false, lm:false, mtf:8,  kg:0.5, thread:72,  price:360,  est:true, format:"X"  },
  { brand:"Samyang", model:"100mm f/2.8 Macro",     type:"P", flMin:100, flMax:100, ap:2.8,  ois:false, wr:false, lm:false, mtf:6,  kg:0.7, thread:67,  price:500,  est:true, format:"X"  },
  { brand:"Samyang", model:"135mm f/2",             type:"P", flMin:135, flMax:135, ap:2.0,  ois:false, wr:false, lm:false, mtf:9,  kg:0.8, thread:77,  price:180,  est:true, format:"X"  },
  { brand:"Samyang", model:"Tilt/Shift 24mm f/3.5", type:"P", flMin:24,  flMax:24,  ap:3.5,  ois:false, wr:false, lm:false, mtf:9,  kg:0.8, thread:82,  price:230,  est:true, format:"X"  },
  // Venus Laowa
  { brand:"Venus Laowa", model:"9mm f2.8 ZeroD",          type:"P", flMin:9,   flMax:9,   ap:2.8,  ois:false, wr:false, lm:false, mtf:8,  kg:0.2, thread:49,  price:500,  est:true, format:"X"  },
  { brand:"Venus Laowa", model:"15mm f/4.5 Zero-D Shift", type:"P", flMin:15,  flMax:15,  ap:4.5,  ois:false, wr:false, lm:false, mtf:8,  kg:0.4, thread:82,  price:800,  est:true, format:"X"  },
  // TTartisan
  { brand:"TTartisan", model:"Tilt 50mm f/1.4",           type:"P", flMin:50,  flMax:50,  ap:1.4,  ois:false, wr:false, lm:false, mtf:6,  kg:0.452, thread:62, price:250, est:true, format:"X"  },
  { brand:"TTartisan", model:"Tilt 35mm f/1.4",           type:"P", flMin:35,  flMax:35,  ap:1.4,  ois:false, wr:false, lm:false, mtf:6,  kg:0.346, thread:52, price:155, est:true, format:"X"  },

  // ── Sigma DC DN Contemporary (AF) ──────────────────────────────────────────
  { brand:"Sigma", model:"16mm f/1.4 DC DN C",   type:"P", flMin:16, flMax:16,  ap:1.4,  ois:false, wr:false, lm:true, mtf:8, kg:0.405, thread:67, price:420, est:true, format:"X", af:true },
  { brand:"Sigma", model:"30mm f/1.4 DC DN C",   type:"P", flMin:30, flMax:30,  ap:1.4,  ois:false, wr:false, lm:true, mtf:8, kg:0.265, thread:52, price:310, est:true, format:"X", af:true },
  { brand:"Sigma", model:"56mm f/1.4 DC DN C",   type:"P", flMin:56, flMax:56,  ap:1.4,  ois:false, wr:false, lm:true, mtf:9, kg:0.280, thread:55, price:440, est:true, format:"X", af:true },
  { brand:"Sigma", model:"18-50mm f/2.8 DC DN C",type:"Z", flMin:18, flMax:50,  ap:2.8,  ois:false, wr:false, lm:true, mtf:8, kg:0.290, thread:52, price:510, est:true, format:"X", af:true },

  // ── Tamron Di III-A (AF) ────────────────────────────────────────────────────
  { brand:"Tamron", model:"11-20mm f/2.8 Di III-A RXD",     type:"Z", flMin:11, flMax:20,  ap:2.8,  ois:false, wr:true, lm:true, mtf:8, kg:0.335, thread:67, price:460, est:true, format:"X", af:true },
  { brand:"Tamron", model:"17-70mm f/2.8 Di III-A VC RXD",  type:"Z", flMin:17, flMax:70,  ap:2.8,  ois:true,  wr:true, lm:true, mtf:8, kg:0.525, thread:67, price:650, est:true, format:"X", af:true },
  { brand:"Tamron", model:"18-300mm f/3.5-6.3 Di III-A VC VXD",type:"Z",flMin:18,flMax:300,ap:3.5, ois:true,  wr:true, lm:true, mtf:7, kg:0.620, thread:67, price:700, est:true, format:"X", af:true },

  // ── Viltrox AF ──────────────────────────────────────────────────────────────
  { brand:"Viltrox", model:"AF 13mm f/1.4 STM",    type:"P", flMin:13, flMax:13,  ap:1.4,  ois:false, wr:false, lm:true, mtf:8, kg:0.410, thread:67, price:460, est:true, format:"X", af:true },
  { brand:"Viltrox", model:"AF 23mm f/1.4 STM",    type:"P", flMin:23, flMax:23,  ap:1.4,  ois:false, wr:false, lm:true, mtf:8, kg:0.224, thread:52, price:250, est:true, format:"X", af:true },
  { brand:"Viltrox", model:"AF 33mm f/1.4 STM",    type:"P", flMin:33, flMax:33,  ap:1.4,  ois:false, wr:false, lm:true, mtf:8, kg:0.224, thread:52, price:250, est:true, format:"X", af:true },
  { brand:"Viltrox", model:"AF 56mm f/1.4 STM",    type:"P", flMin:56, flMax:56,  ap:1.4,  ois:false, wr:false, lm:true, mtf:9, kg:0.216, thread:52, price:270, est:true, format:"X", af:true },
  { brand:"Viltrox", model:"AF 27mm f/1.2 Pro",    type:"P", flMin:27, flMax:27,  ap:1.2,  ois:false, wr:true,  lm:true, mtf:9, kg:0.560, thread:67, price:560, est:true, format:"X", af:true },
  { brand:"Viltrox", model:"AF 75mm f/1.2 Pro",    type:"P", flMin:75, flMax:75,  ap:1.2,  ois:false, wr:true,  lm:true, mtf:9, kg:0.670, thread:77, price:750, est:true, format:"X", af:true },

  // ── Sirui Sniper (AF) ───────────────────────────────────────────────────────
  { brand:"Sirui", model:"Sniper 23mm f/1.2",  type:"P", flMin:23, flMax:23,  ap:1.2,  ois:false, wr:false, lm:true, mtf:7, kg:0.380, thread:58, price:320, est:true, format:"X", af:true },
  { brand:"Sirui", model:"Sniper 33mm f/1.2",  type:"P", flMin:33, flMax:33,  ap:1.2,  ois:false, wr:false, lm:true, mtf:7, kg:0.398, thread:58, price:320, est:true, format:"X", af:true },
  { brand:"Sirui", model:"Sniper 56mm f/1.2",  type:"P", flMin:56, flMax:56,  ap:1.2,  ois:false, wr:false, lm:true, mtf:8, kg:0.419, thread:58, price:320, est:true, format:"X", af:true },

  // ── Tokina atx-m (AF) ───────────────────────────────────────────────────────
  { brand:"Tokina", model:"atx-m 23mm f/1.4 X", type:"P", flMin:23, flMax:23,  ap:1.4,  ois:false, wr:false, lm:true, mtf:8, kg:0.285, thread:52, price:400, est:true, format:"X", af:true },
  { brand:"Tokina", model:"atx-m 33mm f/1.4 X", type:"P", flMin:33, flMax:33,  ap:1.4,  ois:false, wr:false, lm:true, mtf:8, kg:0.270, thread:52, price:350, est:true, format:"X", af:true },
  { brand:"Tokina", model:"atx-m 56mm f/1.4 X", type:"P", flMin:56, flMax:56,  ap:1.4,  ois:false, wr:false, lm:true, mtf:8, kg:0.315, thread:52, price:400, est:true, format:"X", af:true },
  { brand:"Tokina", model:"atx-m 11-18mm f/2.8 X",type:"Z",flMin:11, flMax:18,  ap:2.8,  ois:false, wr:false, lm:true, mtf:8, kg:0.320, thread:67, price:550, est:true, format:"X", af:true },

  // ── TTartisan AF ────────────────────────────────────────────────────────────
  { brand:"TTartisan", model:"AF 27mm f/2.8",  type:"P", flMin:27, flMax:27,  ap:2.8,  ois:false, wr:false, lm:true, mtf:7, kg:0.095, thread:39, price:110, est:true, format:"X", af:true },

  // ── Voigtländer Nokton / Ultron (X-mount) ───────────────────────────────────
  { brand:"Voigtländer", model:"Nokton 23mm f/1.2",  type:"P", flMin:23, flMax:23,  ap:1.2, ois:false, wr:false, lm:false, mtf:8, kg:0.214, thread:46, price:650, est:true, format:"X" },
  { brand:"Voigtländer", model:"Nokton 35mm f/1.2",  type:"P", flMin:35, flMax:35,  ap:1.2, ois:false, wr:false, lm:false, mtf:8, kg:0.196, thread:46, price:600, est:true, format:"X" },
  { brand:"Voigtländer", model:"Nokton 50mm f/1.2",  type:"P", flMin:50, flMax:50,  ap:1.2, ois:false, wr:false, lm:false, mtf:8, kg:0.492, thread:52, price:700, est:true, format:"X" },
  { brand:"Voigtländer", model:"Ultron 27mm f/2",    type:"P", flMin:27, flMax:27,  ap:2.0, ois:false, wr:false, lm:false, mtf:8, kg:0.120, thread:39, price:500, est:true, format:"X" },

  // ── NiSi ────────────────────────────────────────────────────────────────────
  { brand:"NiSi", model:"9mm f/2.8 Sunstar",         type:"P", flMin:9,  flMax:9,   ap:2.8, ois:false, wr:true,  lm:false, mtf:8, kg:0.364, thread:67, price:420, est:true, format:"X" },

  // ── Mitakon / Zhongyi Optics ────────────────────────────────────────────────
  { brand:"Mitakon", model:"Speedmaster 35mm f/0.95 Mk II", type:"P", flMin:35, flMax:35, ap:0.95, ois:false, wr:false, lm:false, mtf:6, kg:0.460, thread:55, price:680, est:true, format:"X" },
  { brand:"Mitakon", model:"Speedmaster 50mm f/0.95",       type:"P", flMin:50, flMax:50, ap:0.95, ois:false, wr:false, lm:false, mtf:6, kg:0.480, thread:55, price:640, est:true, format:"X" },
  { brand:"Mitakon", model:"20mm f/2.4 4.5x Macro",         type:"P", flMin:20, flMax:20, ap:2.4,  ois:false, wr:false, lm:false, mtf:6, kg:0.180, thread:43, price:180, est:true, format:"X" },

  // ── SLR Magic ───────────────────────────────────────────────────────────────
  { brand:"SLR Magic", model:"HyperPrime 50mm T0.95 CINE", type:"P", flMin:50, flMax:50, ap:0.95, ois:false, wr:false, lm:false, mtf:6, kg:0.600, thread:62, price:770, est:true, format:"X" },

  // ── Pergear ─────────────────────────────────────────────────────────────────
  { brand:"Pergear", model:"10mm f/8 Fisheye",  type:"P", flMin:10, flMax:10, ap:8.0,  ois:false, wr:false, lm:false, mtf:5, kg:0.070, thread:0,  price:65,  est:true, format:"X" },
  { brand:"Pergear", model:"25mm f/1.8",        type:"P", flMin:25, flMax:25, ap:1.8,  ois:false, wr:false, lm:false, mtf:6, kg:0.195, thread:43, price:65,  est:true, format:"X" },
  { brand:"Pergear", model:"35mm f/1.6",        type:"P", flMin:35, flMax:35, ap:1.6,  ois:false, wr:false, lm:false, mtf:7, kg:0.185, thread:43, price:90,  est:true, format:"X" },

  // ── Lensbaby ─────────────────────────────────────────────────────────────────
  { brand:"Lensbaby", model:"Velvet 56mm f/1.6 Macro",       type:"P", flMin:56, flMax:56, ap:1.6, ois:false, wr:false, lm:false, mtf:6, kg:0.400, thread:67, price:360, est:true, format:"X" },
  { brand:"Lensbaby", model:"Velvet 85mm f/1.8",             type:"P", flMin:85, flMax:85, ap:1.8, ois:false, wr:false, lm:false, mtf:6, kg:0.500, thread:72, price:440, est:true, format:"X" },
  { brand:"Lensbaby", model:"Composer Pro II Sweet 35 f/2.5",type:"P", flMin:35, flMax:35, ap:2.5, ois:false, wr:false, lm:false, mtf:5, kg:0.200, thread:46, price:310, est:true, format:"X" },
  { brand:"Lensbaby", model:"5.8mm Circular Fisheye f/3.5",  type:"P", flMin:6,  flMax:6,  ap:3.5, ois:false, wr:false, lm:false, mtf:6, kg:0.190, thread:0,  price:180, est:true, format:"X" },

  // ── Thingyfy ─────────────────────────────────────────────────────────────────
  { brand:"Thingyfy", model:"Pinhole Pro X", type:"P", flMin:18, flMax:18, ap:96, ois:false, wr:false, lm:false, mtf:3, kg:0.040, thread:39, price:140, est:true, format:"X" },

  // ── Missing XF / XC ───────────────────────────────────────────────────────
  { brand:"Fujifilm", model:"xf 8mm f/3.5 R WR",          type:"P", flMin:8,   flMax:8,   ap:3.5,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.18,  thread:62,  price:460,   est:false, format:"X", sweetSpot:"f/8"  },
  { brand:"Fujifilm", model:"xf 16mm f/2.8",              type:"P", flMin:16,  flMax:16,  ap:2.8,  ois:false, wr:true,  lm:true,  mtf:8,  kg:0.075, thread:43,  price:310,   est:false, format:"X", sweetSpot:"f/4"  },
  { brand:"Fujifilm", model:"xf 23mm f/2.8 R WR",         type:"P", flMin:23,  flMax:23,  ap:2.8,  ois:false, wr:true,  lm:false, mtf:8,  kg:0.135, thread:43,  price:280,   est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 27mm f/2.8 R WR",         type:"P", flMin:27,  flMax:27,  ap:2.8,  ois:false, wr:true,  lm:false, mtf:8,  kg:0.084, thread:39,  price:260,   est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 56mm f/1.2 R WR",         type:"P", flMin:56,  flMax:56,  ap:1.2,  ois:false, wr:true,  lm:true,  mtf:9,  kg:0.445, thread:62,  price:750,  est:false, format:"X", sweetSpot:"f/2.8"  },
  { brand:"Fujifilm", model:"xc 35mm f/2",                type:"P", flMin:35,  flMax:35,  ap:2.0,  ois:false, wr:false, lm:false, mtf:7,  kg:0.13,  thread:43,  price:200,   est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 16-50mm f/2.8-4.8 R LM WR",type:"Z",flMin:16, flMax:50,  ap:2.8,  ois:false, wr:true,  lm:true,  mtf:8,  kg:0.40,  thread:72,  price:900,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 16-80mm f/4 R OIS WR",    type:"Z", flMin:16,  flMax:80,  ap:4.0,  ois:true,  wr:true,  lm:false, mtf:8,  kg:0.44,  thread:72,  price:600,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 18-120mm f/4 LM PZ WR",   type:"Z", flMin:18,  flMax:120, ap:4.0,  ois:false, wr:true,  lm:true,  mtf:7,  kg:0.46,  thread:72,  price:850,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 70-300mm f/4-5.6 R LM OIS WR",type:"Z",flMin:70,flMax:300,ap:4.0, ois:true,  wr:true,  lm:true,  mtf:8,  kg:0.58,  thread:72,  price:800,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"xf 150-600mm f/5.6-8 R LM OIS WR",type:"Z",flMin:150,flMax:600,ap:5.6,ois:true, wr:true,  lm:true,  mtf:8,  kg:1.605, thread:95,  price:1400,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"mkx 18-55mm T2.9",           type:"Z", flMin:18,  flMax:55,  ap:2.8,  ois:true,  wr:false, lm:true,  mtf:8,  kg:0.98,  thread:82,  price:2000,  est:false, format:"X"  },
  { brand:"Fujifilm", model:"mkx 50-135mm T2.9",          type:"Z", flMin:50,  flMax:135, ap:2.8,  ois:true,  wr:false, lm:true,  mtf:8,  kg:1.12,  thread:82,  price:2300,  est:false, format:"X"  },

  // ── GF / G-Mount (Medium Format, crop 0.79×) ──────────────────────────────
  { brand:"Fujifilm", model:"gf 23mm f/4 R LM WR",        type:"P", flMin:23,  flMax:23,  ap:4.0,  ois:false, wr:true,  lm:true,  mtf:9,  kg:0.845, thread:82,  price:1400,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 30mm f/3.5 R WR",         type:"P", flMin:30,  flMax:30,  ap:3.5,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.51,  thread:58,  price:850,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 45mm f/2.8 R WR",         type:"P", flMin:45,  flMax:45,  ap:2.8,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.49,  thread:62,  price:1100,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 50mm f/3.5 R LM WR",      type:"P", flMin:50,  flMax:50,  ap:3.5,  ois:false, wr:true,  lm:true,  mtf:9,  kg:0.335, thread:62,  price:410,   est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 55mm f/1.7 R WR",         type:"P", flMin:55,  flMax:55,  ap:1.7,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.62,  thread:77,  price:1450,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 63mm f/2.8 R WR",         type:"P", flMin:63,  flMax:63,  ap:2.8,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.405, thread:62,  price:1000,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 80mm f/1.7 R WR",         type:"P", flMin:80,  flMax:80,  ap:1.7,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.795, thread:77,  price:1300,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 110mm f/2 R LM WR",       type:"P", flMin:110, flMax:110, ap:2.0,  ois:false, wr:true,  lm:true,  mtf:10, kg:1.0,   thread:77,  price:1850,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 200mm f/2 R LM OIS WR",   type:"P", flMin:200, flMax:200, ap:2.0,  ois:true,  wr:true,  lm:true,  mtf:10, kg:3.4,   thread:95,  price:4100,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 250mm f/4 R LM OIS WR",   type:"P", flMin:250, flMax:250, ap:4.0,  ois:true,  wr:true,  lm:true,  mtf:9,  kg:1.535, thread:95,  price:2300,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 500mm f/5.6 R LM OIS WR", type:"P", flMin:500, flMax:500, ap:5.6,  ois:true,  wr:true,  lm:true,  mtf:9,  kg:2.1,   thread:95,  price:3600,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 20-35mm f/4 R WR",        type:"Z", flMin:20,  flMax:35,  ap:4.0,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.525, thread:82,  price:1400,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 32-64mm f/4 R LM WR",     type:"Z", flMin:32,  flMax:64,  ap:4.0,  ois:false, wr:true,  lm:true,  mtf:9,  kg:0.875, thread:77,  price:1300,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 35-70mm f/4.5-5.6 WR",    type:"Z", flMin:35,  flMax:70,  ap:4.5,  ois:false, wr:true,  lm:false, mtf:8,  kg:0.39,  thread:62,  price:360,   est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 45-100mm f/4 R LM OIS WR",type:"Z", flMin:45,  flMax:100, ap:4.0,  ois:true,  wr:true,  lm:true,  mtf:9,  kg:1.14,  thread:77,  price:1450,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 100-200mm f/5.6 R LM OIS WR",type:"Z",flMin:100,flMax:200,ap:5.6, ois:true,  wr:true,  lm:true,  mtf:9,  kg:1.055, thread:72,  price:1650,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 30mm f/5.6 T/S",          type:"P", flMin:30,  flMax:30,  ap:5.6,  ois:false, wr:true,  lm:false, mtf:9,  kg:0.88,  thread:82,  price:1800,  est:false, format:"GFX" },
  { brand:"Fujifilm", model:"gf 110mm f/5.6 T/S Macro",   type:"P", flMin:110, flMax:110, ap:5.6,  ois:false, wr:true,  lm:false, mtf:9,  kg:1.05,  thread:82,  price:2000,  est:false, format:"GFX" },

  // ── Third-party GFX (G-Mount) ────────────────────────────────────────────────
  { brand:"Venus Laowa", model:"17mm f/4 Zero-D GFX",      type:"P", flMin:17, flMax:17,  ap:4.0, ois:false, wr:false, lm:false, mtf:7, kg:0.829, thread:86, price:1000, est:true, format:"GFX" },
  { brand:"Venus Laowa", model:"55mm f/2.8 T/S Macro GFX", type:"P", flMin:55, flMax:55,  ap:2.8, ois:false, wr:false, lm:false, mtf:8, kg:0.860, thread:82, price:1100, est:true, format:"GFX" },
  { brand:"Venus Laowa", model:"100mm f/2.8 T/S Macro GFX",type:"P", flMin:100,flMax:100, ap:2.8, ois:false, wr:false, lm:false, mtf:8, kg:1.200, thread:82, price:1200, est:true, format:"GFX" },
  { brand:"Mitakon",     model:"Speedmaster 65mm f/1.4 GFX",type:"P", flMin:65, flMax:65,  ap:1.4, ois:false, wr:false, lm:false, mtf:7, kg:1.050, thread:72, price:650,  est:true, format:"GFX" },
  { brand:"Irix",        model:"45mm f/1.4 Dragonfly GFX", type:"P", flMin:45, flMax:45,  ap:1.4, ois:false, wr:true,  lm:false, mtf:8, kg:1.120, thread:77, price:360,  est:true, format:"GFX" },
  { brand:"TTartisan",   model:"11mm f/2.8 Fisheye GFX",   type:"P", flMin:11, flMax:11,  ap:2.8, ois:false, wr:false, lm:false, mtf:5, kg:0.280, thread:0,  price:195,  est:true, format:"GFX" },
  { brand:"TTartisan",   model:"90mm f/1.25 GFX",          type:"P", flMin:90, flMax:90,  ap:1.25,ois:false, wr:false, lm:false, mtf:6, kg:1.040, thread:77, price:410,  est:true, format:"GFX" },
  { brand:"TTartisan",   model:"100mm f/2.8 Macro 2X GFX", type:"P", flMin:100,flMax:100, ap:2.8, ois:false, wr:false, lm:false, mtf:7, kg:0.600, thread:67, price:365,  est:true, format:"GFX" },
  { brand:"AstrHori",    model:"55mm f/5.6 GFX",            type:"P", flMin:55, flMax:55,  ap:5.6, ois:false, wr:false, lm:false, mtf:7, kg:0.350, thread:62, price:365,  est:true, format:"GFX" },
  { brand:"AstrHori",    model:"75mm f/4 GFX",              type:"P", flMin:75, flMax:75,  ap:4.0, ois:false, wr:false, lm:false, mtf:7, kg:0.634, thread:67, price:365,  est:true, format:"GFX" },
  { brand:"Kipon",       model:"IBERIT 75mm f/2.4 GFX",     type:"P", flMin:75, flMax:75,  ap:2.4, ois:false, wr:false, lm:false, mtf:7, kg:0.270, thread:49, price:320,  est:true, format:"GFX" },

  // ── NiSi Athena Prime Cinema (G-Mount) ──────────────────────────────────────
  { brand:"NiSi", model:"Athena 14mm T2.4 GFX",  type:"P", flMin:14,  flMax:14,  ap:2.4, ois:false, wr:false, lm:false, mtf:8, kg:0.820, thread:0,  price:1050, est:true, format:"GFX" },
  { brand:"NiSi", model:"Athena 18mm T2.2 GFX",  type:"P", flMin:18,  flMax:18,  ap:2.2, ois:false, wr:false, lm:false, mtf:8, kg:0.800, thread:77, price:1050, est:true, format:"GFX" },
  { brand:"NiSi", model:"Athena 25mm T1.9 GFX",  type:"P", flMin:25,  flMax:25,  ap:1.9, ois:false, wr:false, lm:false, mtf:8, kg:0.800, thread:77, price:1050, est:true, format:"GFX" },
  { brand:"NiSi", model:"Athena 35mm T1.9 GFX",  type:"P", flMin:35,  flMax:35,  ap:1.9, ois:false, wr:false, lm:false, mtf:8, kg:0.800, thread:77, price:1050, est:true, format:"GFX" },
  { brand:"NiSi", model:"Athena 40mm T1.9 GFX",  type:"P", flMin:40,  flMax:40,  ap:1.9, ois:false, wr:false, lm:false, mtf:8, kg:0.800, thread:77, price:1050, est:true, format:"GFX" },
  { brand:"NiSi", model:"Athena 50mm T1.9 GFX",  type:"P", flMin:50,  flMax:50,  ap:1.9, ois:false, wr:false, lm:false, mtf:8, kg:0.800, thread:77, price:1050, est:true, format:"GFX" },
  { brand:"NiSi", model:"Athena 85mm T1.9 GFX",  type:"P", flMin:85,  flMax:85,  ap:1.9, ois:false, wr:false, lm:false, mtf:8, kg:0.800, thread:77, price:1050, est:true, format:"GFX" },
  { brand:"NiSi", model:"Athena 135mm T2.2 GFX", type:"P", flMin:135, flMax:135, ap:2.2, ois:false, wr:false, lm:false, mtf:8, kg:1.100, thread:77, price:1150, est:true, format:"GFX" },
  { brand:"AstrHori",    model:"75mm f/4 GFX",             type:"P", flMin:75, flMax:75,  ap:4.0, ois:false, wr:false, lm:false, mtf:7, kg:0.635, thread:67, price:140,  est:true, format:"GFX" },
];

const TRADE = [
  { model:"7artisans 55mm f1.4",       newPrice:208,  usedPrice:200,  savings:8,    ratio:0.04 },
  { model:"Kamlan 50mm f1.1",          newPrice:300,  usedPrice:330,  savings:-30,  ratio:-0.09},
  { model:"Samyang 21/1.4",            newPrice:800,  usedPrice:800,  savings:0,    ratio:0 },
  { model:"XC 15-45mm f/3.5-5.6 OIS", newPrice:590,  usedPrice:400,  savings:190,  ratio:0.475},
  { model:"XC 16-50mm f/3.5-5.6 OIS", newPrice:780,  usedPrice:250,  savings:530,  ratio:2.12, top:true },
  { model:"XC 50-230mm f/4.5-6.7",    newPrice:800,  usedPrice:280,  savings:520,  ratio:1.857,top:true },
  { model:"XF 100-400mm f/4.5-5.6",   newPrice:3600, usedPrice:2800, savings:800,  ratio:0.286},
  { model:"XF 14mm f/2.8",            newPrice:1850, usedPrice:750,  savings:1100, ratio:1.467,top:true },
  { model:"XF 16-55mm f/2.8 R LM WR", newPrice:2300, usedPrice:1380, savings:920,  ratio:0.667},
  { model:"XF 16-80mm f/4.0",         newPrice:1650, usedPrice:1300, savings:350,  ratio:0.269},
  { model:"XF 16mm f/1.4",            newPrice:2150, usedPrice:900,  savings:1250, ratio:1.389,top:true },
  { model:"XF 18-135mm f/3.5-5.6",    newPrice:1570, usedPrice:650,  savings:920,  ratio:1.415,top:true },
  { model:"XF 18-55mm f/2.8-4 OIS",   newPrice:1223, usedPrice:500,  savings:723,  ratio:1.446,top:true },
  { model:"XF 18mm f/2",              newPrice:1200, usedPrice:550,  savings:650,  ratio:1.182,top:true },
  { model:"XF 23mm f/2.0",            newPrice:980,  usedPrice:600,  savings:380,  ratio:0.633},
  { model:"XF 23mm f/1.4",            newPrice:1800, usedPrice:1300, savings:500,  ratio:0.385},
  { model:"XF 27mm f/2.8",            newPrice:880,  usedPrice:350,  savings:530,  ratio:1.514,top:true },
  { model:"XF 50-140mm f/2.8 R LM OIS",newPrice:3150,usedPrice:2100, savings:1050, ratio:0.5,  priority:1 },
  { model:"XF 50mm f/2.0",            newPrice:980,  usedPrice:650,  savings:330,  ratio:0.508},
  { model:"XF 55-200mm f/3.5-4.8",    newPrice:1470, usedPrice:1150, savings:320,  ratio:0.278 },
  { model:"XF 56mm f/1.2",            newPrice:2000, usedPrice:1200, savings:800,  ratio:0.667 },
  { model:"XF 60mm f/2.4 Macro",      newPrice:1370, usedPrice:500,  savings:870,  ratio:1.74, top:true },
  { model:"XF 90mm f/2.0",            newPrice:1600, usedPrice:1050, savings:550,  ratio:0.524 },
  { model:"Zeiss Touit 2.8/12",        newPrice:1800, usedPrice:1100, savings:700,  ratio:0.636},
  { model:"Zeiss Touit 2.8/50",        newPrice:1700, usedPrice:1300, savings:400,  ratio:0.308},
];

const GENRES = [
  { genre:"Astronomy",     brand:"Fujifilm",    model:"xf 16mm f/1.4",          fl:16,  top:true  },
  { genre:"Astronomy",     brand:"Meike",       model:"25mm f0.95",              fl:25,  top:false },
  { genre:"Astronomy",     brand:"Meike",       model:"6.5mm Fisheye f2.0",      fl:6,   top:false },
  { genre:"Astronomy",     brand:"Samyang",     model:"8mm f/2.8",               fl:8,   top:false },
  { genre:"Astronomy",     brand:"Samyang",     model:"12mm f/2",                fl:12,  top:false },
  { genre:"Astronomy",     brand:"Samyang",     model:"21mm F1.4",               fl:21,  top:true  },
  { genre:"Landscape",     brand:"Fujifilm",    model:"xf 14mm f/2.8",           fl:14,  top:false },
  { genre:"Landscape",     brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS WR",      fl:16,  top:true  },
  { genre:"Landscape",     brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS",         fl:16,  top:false },
  { genre:"Landscape",     brand:"Samyang",     model:"16mm f/2",                fl:16,  top:false },
  { genre:"Landscape",     brand:"Fujifilm",    model:"xf 90mm f/2.0",           fl:90,  top:true  },
  { genre:"Landscape",     brand:"Fujifilm",    model:"xf 100-400mm f/4.5-5.6",  fl:250, top:true  },
  { genre:"Landscape",     brand:"Samyang",     model:"135mm f/2",               fl:135, top:false },
  { genre:"Architecture",  brand:"Fujifilm",    model:"xf 14mm f/2.8",           fl:14,  top:false },
  { genre:"Architecture",  brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS WR",      fl:16,  top:true  },
  { genre:"Architecture",  brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS",         fl:16,  top:false },
  { genre:"Architecture",  brand:"Meike",       model:"6.5mm Fisheye f2.0",      fl:6,   top:false },
  { genre:"Architecture",  brand:"Samyang",     model:"16mm f/2",                fl:16,  top:false },
  { genre:"Architecture",  brand:"Samyang",     model:"21mm F1.4",               fl:21,  top:true  },
  { genre:"Architecture",  brand:"Samyang",     model:"Tilt/Shift 24mm f/3.5",   fl:24,  top:false },
  { genre:"Street",        brand:"Samyang",     model:"35mm f/1.2",              fl:35,  top:false },
  { genre:"Street",        brand:"Meike",       model:"25mm f0.95",              fl:25,  top:false },
  { genre:"Street",        brand:"Fujifilm",    model:"xf 16mm f/1.4",           fl:16,  top:true  },
  { genre:"Street",        brand:"Fujifilm",    model:"xf 23mm f/1.4",           fl:23,  top:false },
  { genre:"Street",        brand:"Samyang",     model:"21mm F1.4",               fl:21,  top:true  },
  { genre:"Street",        brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS WR",      fl:16,  top:true  },
  { genre:"Street",        brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS",         fl:16,  top:false },
  { genre:"Travel",        brand:"Fujifilm",    model:"xf 16mm f/1.4",           fl:16,  top:true  },
  { genre:"Travel",        brand:"Fujifilm",    model:"xf 23mm f/1.4",           fl:23,  top:false },
  { genre:"Travel",        brand:"Fujifilm",    model:"xf 18-55mm f/2.8-4.0",    fl:35,  top:false },
  { genre:"Travel",        brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS WR",      fl:16,  top:true  },
  { genre:"Travel",        brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS",         fl:16,  top:false },
  { genre:"Travel",        brand:"Samyang",     model:"35mm f/1.2",              fl:35,  top:false },
  { genre:"Travel",        brand:"Samyang",     model:"21mm F1.4",               fl:21,  top:true  },
  { genre:"Portrait",      brand:"Fujifilm",    model:"xf 16mm f/1.4",           fl:16,  top:true  },
  { genre:"Portrait",      brand:"Fujifilm",    model:"xf 23mm f/2.0",           fl:23,  top:false },
  { genre:"Portrait",      brand:"Fujifilm",    model:"xf 35mm f/1.4",           fl:35,  top:false },
  { genre:"Portrait",      brand:"Fujifilm",    model:"xf 50mm f/2.0",           fl:50,  top:false },
  { genre:"Portrait",      brand:"Fujifilm",    model:"xf 56mm f/1.2",           fl:56,  top:false },
  { genre:"Portrait",      brand:"Fujifilm",    model:"xf 90mm f/2.0",           fl:90,  top:true  },
  { genre:"Sport",         brand:"Fujifilm",    model:"xf 80mm f/2.8 Macro",     fl:80,  top:false },
  { genre:"Sport",         brand:"Fujifilm",    model:"xf 90mm f/2.0",           fl:90,  top:true  },
  { genre:"Sport",         brand:"Fujifilm",    model:"xf 50-140mm f/2.8",       fl:90,  top:false },
  { genre:"Sport",         brand:"Fujifilm",    model:"xf 55-200mm f/3.5-4.8",   fl:135, top:false },
  { genre:"Sport",         brand:"Fujifilm",    model:"xf 100-400mm f/4.5-5.6",  fl:250, top:true  },
  { genre:"Sport",         brand:"Fujifilm",    model:"xc 50-230mm f/4.5-6.7",   fl:135, top:false },
  { genre:"Wildlife",      brand:"Fujifilm",    model:"xf 200mm f/2.0",          fl:200, top:false },
  { genre:"Wildlife",      brand:"Fujifilm",    model:"xf 90mm f/2.0",           fl:90,  top:true  },
  { genre:"Wildlife",      brand:"Fujifilm",    model:"xf 50-140mm f/2.8",       fl:90,  top:false },
  { genre:"Wildlife",      brand:"Fujifilm",    model:"xf 55-200mm f/3.5-4.8",   fl:135, top:false },
  { genre:"Wildlife",      brand:"Fujifilm",    model:"xf 100-400mm f/4.5-5.6",  fl:250, top:true  },
  { genre:"Wildlife",      brand:"Samyang",     model:"135mm f/2",               fl:135, top:false },
];

const GENRE_LIST = ["Astronomy","Landscape","Architecture","Street","Travel","Portrait","Sport","Wildlife"];

const ISO_STEPS = [100, 200, 400, 800, 1600, 3200, 6400];
const FL_STEPS  = [12, 14, 16, 18, 21, 24, 28, 35, 50, 70, 85, 100, 135, 200, 300, 400, 500, 600];

// ─── EV DATA ──────────────────────────────────────────────────────────────────

const EV_SCENES = [
  {ev:18,  short:"Bright reflections"},
  {ev:17,  short:"White in bright sun"},
  {ev:16,  short:"Sand or snow"},
  {ev:15,  short:"Bright or hazy sun"},
  {ev:14,  short:"Slightly overcast"},
  {ev:13,  short:"Overcast"},
  {ev:12,  short:"Heavy overcast"},
  {ev:11,  short:"Sunset / deep shade"},
  {ev:10,  short:"Just after sunset"},
  {ev:9,   short:"10 min after sunset"},
  {ev:8,   short:"Times Square at night"},
  {ev:7,   short:"Bright street at night"},
  {ev:6,   short:"Night interior (bright)"},
  {ev:5,   short:"Night interior (average)"},
  {ev:4,   short:"Bright street lamps"},
  {ev:3,   short:"Brightly lit night streets"},
  {ev:2,   short:"Typical night streets"},
  {ev:1,   short:"City sky"},
  {ev:0,   short:"Bright suburban sky"},
  {ev:-1,  short:"Suburban sky"},
  {ev:-2,  short:"Full moon on snow"},
  {ev:-3,  short:"Full moon landscape"},
  {ev:-4,  short:"Half moon landscape"},
  {ev:-5,  short:"Crescent moon"},
  {ev:-6,  short:"Starlight landscape"},
  {ev:-7,  short:"Milky Way"},
  {ev:-8,  short:"Deep sky"},
];

// Per-genre scene label overrides — keyed by EV value
const GENRE_EV_LABELS = {
  Landscape: {
    16: "Snow field / bright beach",
    15: "Sunny open landscape",
    14: "Thin overcast",
    13: "Overcast sky",
    12: "Heavy overcast",
    11: "Mountain peaks at golden hour",
    10: "Lake reflection at dusk",
     9: "Coastal cliffs at blue hour",
     8: "Forest ridgeline at late twilight",
     7: "Dark valley / mountain silhouette",
  },
  Architecture: {
     12: "Overcast exterior",
     11: "Golden hour / open shade",
     10: "Deep shade / glass atrium",
      9: "Bright interior / skylights",
      8: "Blue hour",
      7: "Indoor daylight",
      6: "Office / lobby",
      5: "Dim church / museum",
      4: "Night exterior",
      3: "Night interior",
  },
  Street: {
     8: "Bright overcast city",
     7: "Open shade / cloudy",
     6: "Overcast street",
     5: "Covered market / indoor street",
     4: "Dusk / golden hour",
     3: "Late evening urban",
     2: "Night market / bright signage",
     1: "Lit street at night",
     0: "Night street, neon signs",
    [-1]: "Deep night, single streetlamp",
  },
  Travel: {
    14: "Bright beach / snow",
    13: "Sunny open square",
    12: "Hazy sun / open shade",
    11: "Partly cloudy",
    10: "Overcast exterior",
     9: "Covered market / arcade",
     8: "Bright interior / atrium",
     7: "Dim interior / café",
     6: "Blue hour / dusk",
     5: "Golden hour street",
  },
  Portrait: {
    14: "Bright sun / outdoor midday",
    13: "Slightly overcast",
    12: "Open shade / slight overcast",
    11: "Golden hour",
    10: "Window light",
     9: "Blue hour / shade",
     8: "Overcast exterior",
     7: "Bright interior / studio",
     6: "Indoor natural light",
     5: "Dim interior / candlelight",
  },
  Sport: {
    16: "Bright sun / stadium",
    15: "Sunny outdoor",
    14: "Slightly overcast",
    13: "Overcast outdoor",
    12: "Heavy overcast",
    11: "Golden hour",
    10: "Indoor arena (bright)",
     9: "Indoor arena (average)",
     8: "Indoor gym",
     6: "Dim indoor / swimming",
  },
  Wildlife: {
    14: "Bright sun / open field",
    13: "Slightly overcast",
    12: "Open shade",
    11: "Golden hour",
    10: "Sunset",
     9: "Blue hour",
     8: "Forest clearing",
     7: "Dense forest",
     6: "Dusk / low light",
     5: "Near darkness",
  },
};

// min shutter = handheld limit or motion-freeze limit per genre
const GENRE_PARAMS = {
  Astronomy:    {fl:14,  label:"Untracked tripod · Beat the startrails · 500 rule", minShutter:null, rule500:true},
  Landscape:    {fl:8,   label:"Tripod · creative exposure control · peak sharpness", minShutter:1/12},
  Architecture: {fl:14,  label:`Tripod · maximize depth of field · sweet spot at f/8`, minShutter:1/4},
  Street:       {fl:35,  label:"Handheld · capture the moment · 1/FL rule", minShutter:1/60},
  Travel:       {fl:24,  label:"Handheld · light and versatile · 1/FL rule", minShutter:1/36},
  Portrait:     {fl:57,  label:"Handheld · freeze expression · 2× FL rule",                     minShutter:1/85},
  Sport:        {fl:85,  label:"Handheld · freeze motion · 4× FL rule",            minShutter:1/340},
  Wildlife:     {fl:85,  label:"Handheld · capture behaviour · 4× FL rule",        minShutter:1/340},
};

// mark: 1=best, 5=worst. null=no score (use top flag only)
// markOis: score when OIS is considered
const EV_LENSES = {
  Astronomy: [
    {brand:"Meike",       model:"25mm f0.95",              mtf:7, kg:0.6, price:600, mark:5, top:true},
    {brand:"Meike",       model:"6.5mm Fisheye f2.0",      mtf:8, kg:0.3, price:150,  mark:5, top:true},
    {brand:"Fujifilm",    model:"xf 16mm f/1.4",           mtf:8, kg:0.4, price:1000, sweetSpot:"f/4", mark:4, top:true},
    {brand:"Fujifilm",    model:"xf 23mm f/1.4",           mtf:8, kg:0.3, price:950, sweetSpot:"f/4", mark:4, top:false},
    {brand:"Fujifilm",    model:"xf 56mm f/1.2",           mtf:8, kg:0.4, price:900, sweetSpot:"f/5.6", sweetSpot:"f/5.6", mark:4, top:false},
    {brand:"Fujifilm",    model:"xf 8-16mm f/2.8",         mtf:9, kg:0.8, price:2000, sweetSpot:"f/5.6", mark:4, top:false},
    {brand:"Kamlan",      model:"50mm f1.1",               mtf:7, kg:0.3, price:200,  mark:4, top:false},
    {brand:"Samyang",     model:"8mm f/2.8",               mtf:9, kg:0.2, price:310,  mark:4, top:true},
    {brand:"Samyang",     model:"12mm f/2",                mtf:8, kg:0.3, price:410,  mark:4, top:true},
    {brand:"Samyang",     model:"20mm f/1.8",              mtf:7, kg:0.5, price:490,  mark:4, top:false},
    {brand:"Samyang",     model:"21mm F1.4",               mtf:7, kg:0.3, price:410,  mark:4, top:true},
    {brand:"Samyang",     model:"50mm f/1.2",              mtf:8, kg:0.4, price:430,  mark:4, top:false},
    {brand:"7Artisans",   model:"55mm f1.4",               mtf:7, kg:0.3, price:100,  mark:3, top:false},
    {brand:"Fujifilm",    model:"xf 14mm f/2.8",           mtf:8, kg:0.2, price:950, sweetSpot:"f/4", mark:3, top:false},
    {brand:"Fujifilm",    model:"xf 18mm f/2.0",           mtf:7, kg:0.1, price:550, sweetSpot:"f/5.6", mark:3, top:false},
    {brand:"Fujifilm",    model:"xf 23mm f/2.0",           mtf:8, kg:0.2, price:500, sweetSpot:"f/5.6", mark:3, top:false},
    {brand:"Fujifilm",    model:"xf 35mm f/1.4",           mtf:7, kg:0.2, price:600, sweetSpot:"f/4", mark:3, top:false},
    {brand:"Samyang",     model:"10mm f/2.8",              mtf:7, kg:0.6, price:500, mark:3, top:false},
    {brand:"Samyang",     model:"12mm f/2.8",              mtf:7, kg:0.5, price:500, mark:3, top:false},
    {brand:"Samyang",     model:"14mm f/2.8",              mtf:7, kg:0.6, price:410,  mark:3, top:false},
    {brand:"Samyang",     model:"16mm f/2",                mtf:8, kg:0.6, price:460,  mark:3, top:false},
    {brand:"Samyang",     model:"50mm f/1.4",              mtf:7, kg:0.5, price:410,  mark:3, top:false},
    {brand:"Samyang",     model:"8mm f/3.5",               mtf:7, kg:0.4, price:330,  mark:3, top:false},
    {brand:"Venus Laowa", model:"9mm f2.8 ZeroD",          mtf:8, kg:0.2, price:500, mark:3, top:false},
    {brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS WR",      mtf:8, kg:0.4, price:1000, sweetSpot:"f/8", mark:2, top:true},
    {brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS",         mtf:8, kg:0.4, price:410,  sweetSpot:"f/8", mark:2, top:false, est:true},
    {brand:"Fujifilm",    model:"xf 27mm f/2.8",           mtf:7, kg:0.1, price:460,  sweetSpot:"f/5.6", mark:2, top:false},
    {brand:"Fujifilm",    model:"xf 35mm f/2.0",           mtf:7, kg:0.2, price:460,  sweetSpot:"f/4", mark:2, top:false},
    {brand:"Fujifilm",    model:"xf 50mm f/2.0",           mtf:9, kg:0.2, price:500,  sweetSpot:"f/4", mark:2, top:false},
    {brand:"Samyang",     model:"85mm f/1.4",              mtf:8, kg:0.5, price:360,  mark:2, top:false},
    // GF lenses
    {brand:"Fujifilm",    model:"gf 55mm f/1.7 R WR",      mtf:9, kg:0.62, price:1450, sweetSpot:"f/5.6", mark:5, top:true},
    {brand:"Fujifilm",    model:"gf 80mm f/1.7 R WR",      mtf:9, kg:0.795,price:1300, sweetSpot:"f/5.6", mark:5, top:true},
    {brand:"Fujifilm",    model:"gf 30mm f/3.5 R WR",      mtf:9, kg:0.51, price:850, sweetSpot:"f/8", mark:4, top:true},
    {brand:"Fujifilm",    model:"gf 45mm f/2.8 R WR",      mtf:9, kg:0.49, price:1100, sweetSpot:"f/8", mark:4, top:false},
    {brand:"Fujifilm",    model:"gf 63mm f/2.8 R WR",      mtf:9, kg:0.405,price:1000, sweetSpot:"f/5.6", mark:3, top:false},
    {brand:"Fujifilm",    model:"gf 110mm f/2 R LM WR",    mtf:10,kg:1.0,  price:1850, sweetSpot:"f/5.6", mark:3, top:false},
    {brand:"Fujifilm",    model:"gf 23mm f/4 R LM WR",     mtf:9, kg:0.845,price:1400, sweetSpot:"f/8", mark:3, top:false},
    {brand:"Fujifilm",    model:"gf 20-35mm f/4 R WR",     mtf:9, kg:0.525,price:1400, sweetSpot:"f/8", mark:2, top:false},
    {brand:"Fujifilm",    model:"gf 32-64mm f/4 R LM WR",  mtf:9, kg:0.875,price:1300, sweetSpot:"f/8", mark:2, top:false},
  ],
  Street: [
    {brand:"Meike",        model:"25mm f0.95",              mtf:7, kg:0.6, price:600, mark:5, markOis:5, top:true},
    {brand:"7Artisans",    model:"35mm f1.2",               mtf:6, kg:0.2, price:150,  mark:4, markOis:4, top:false},
    {brand:"Mitakon",      model:"35mm f0.95 Mk II",        mtf:6, kg:0.6, price:600, mark:4, markOis:4, top:false},
    {brand:"Samyang",      model:"35mm f/1.2",              mtf:7, kg:0.4, price:410,  mark:4, markOis:4, top:true},
    {brand:"Samyang",      model:"12mm f/2",                mtf:8, kg:0.3, price:410,  mark:4, markOis:4, top:false},
    {brand:"Samyang",      model:"21mm F1.4",               mtf:7, kg:0.3, price:410,  mark:4, markOis:4, top:true},
    {brand:"Samyang",      model:"24mm f/1.4",              mtf:6, kg:0.6, price:650, mark:4, markOis:4, top:false},
    {brand:"Fujifilm",     model:"xf 16mm f/1.4",           mtf:8, kg:0.4, price:1000, sweetSpot:"f/4", mark:4, markOis:4, top:true},
    {brand:"Fujifilm",     model:"xf 23mm f/1.4",           mtf:8, kg:0.3, price:950, sweetSpot:"f/4", mark:4, markOis:4, top:true},
    {brand:"Fujifilm",     model:"xf 56mm f/1.2",           mtf:8, kg:0.4, price:900, sweetSpot:"f/5.6", sweetSpot:"f/5.6", mark:3, markOis:3, top:false},
    {brand:"Kamlan",       model:"50mm f1.1",               mtf:7, kg:0.3, price:200,  mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"50mm f/1.2",              mtf:8, kg:0.4, price:430,  mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xf 35mm f/1.4",           mtf:7, kg:0.2, price:600, sweetSpot:"f/4", mark:3, markOis:3, top:false},
    {brand:"Kamlan",       model:"28mm f1.4",               mtf:6, kg:0.4, price:200,  mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"35mm f/1.4",              mtf:9, kg:0.7, price:500, mark:3, markOis:3, top:false},
    {brand:"7Artisans",    model:"25mm f1.8",               mtf:5, kg:0.2, price:100,  mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xf 18mm f/2.0",           mtf:7, kg:0.1, price:550, sweetSpot:"f/5.6", mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xf 23mm f/2.0",           mtf:8, kg:0.2, price:500, sweetSpot:"f/5.6", mark:3, markOis:3, top:false},
    {brand:"Meike",        model:"25mm f1.8",               mtf:7, kg:0.2, price:100,  mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"16mm f/2",                mtf:8, kg:0.6, price:460,  mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"20mm f/1.8",              mtf:7, kg:0.5, price:490,  mark:3, markOis:3, top:false},
    {brand:"7Artisans",    model:"7.5mm F2.8",              mtf:6, kg:0.3, price:200,  mark:3, markOis:3, top:false},
    {brand:"Carl Zeiss",   model:"Touit 12 mm f/2.8",       mtf:8, kg:0.3, price:900, mark:3, markOis:3, top:false},
    {brand:"Meike",        model:"12mm f2.8",               mtf:6, kg:0.4, price:260,  mark:3, markOis:3, top:false},
    {brand:"Opteka",       model:"12mm f2.8",               mtf:6, kg:0.4, price:260,  mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"10mm f/2.8",              mtf:7, kg:0.6, price:500, mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"12mm f/2.8",              mtf:7, kg:0.5, price:500, mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"8mm f/2.8",               mtf:6, kg:0.2, price:330,  mark:3, markOis:3, top:false},
    {brand:"Venus Laowa",  model:"9mm f2.8 ZeroD",          mtf:8, kg:0.2, price:500, mark:3, markOis:3, top:false},
    {brand:"7Artisans",    model:"55mm f1.4",               mtf:7, kg:0.3, price:100,  mark:2, markOis:2, top:false},
    {brand:"Lensbaby",     model:"Velvet 56 f1.6 Macro",    mtf:6, kg:0.4, price:410,  mark:2, markOis:2, top:false},
    {brand:"Samyang",      model:"50mm f/1.4",              mtf:7, kg:0.5, price:410,  mark:2, markOis:2, top:false},
    {brand:"Meike",        model:"35mm f1.7",               mtf:6, kg:0.2, price:100,  mark:2, markOis:2, top:false},
    {brand:"7Artisans",    model:"35mm f2",                 mtf:5, kg:0.3, price:200,  mark:2, markOis:2, top:false},
    {brand:"Carl Zeiss",   model:"Touit 32 mm f/1.8",       mtf:7, kg:0.2, price:600, mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 35mm f/2.0",           mtf:7, kg:0.2, price:460,  sweetSpot:"f/4", mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 14mm f/2.8",           mtf:8, kg:0.2, price:950, sweetSpot:"f/4", mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 16-55mm f/2.8",        mtf:8, kg:0.7, price:1200, sweetSpot:"f/8", mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 18-55mm f/2.8-4.0 OIS",mtf:7, kg:0.3, price:750, sweetSpot:"f/8", mark:2, markOis:4, top:false},
    {brand:"Handevision",  model:"IBERIT 24mm f2.4",        mtf:7, kg:0.5, price:600, mark:2, markOis:2, top:false},
    {brand:"Mitakon",      model:"20mm f2.4 4.5x Macro",    mtf:6, kg:0.2, price:200,  mark:2, markOis:2, top:false},
    {brand:"Samyang",      model:"14mm f/2.8",              mtf:7, kg:0.6, price:410,  mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 8-16mm f/2.8",         mtf:9, kg:0.8, price:2000, sweetSpot:"f/5.6", mark:2, markOis:4, top:false},
    {brand:"Fujifilm",     model:"xf 10-24mm f/4 R OIS WR",      mtf:8, kg:0.4, price:1000, sweetSpot:"f/8", mark:2, markOis:4, top:true},
    {brand:"Fujifilm",     model:"xf 10-24mm f/4 R OIS",         mtf:8, kg:0.4, price:410,  sweetSpot:"f/8", mark:2, markOis:4, top:false, est:true},
    {brand:"Meike",        model:"8mm Fisheye f3.5",        mtf:7, kg:0.5, price:200,  mark:2, markOis:2, top:false},
    {brand:"Samyang",      model:"8mm f/3.5",               mtf:6, kg:0.4, price:330,  mark:2, markOis:2, top:false},
    {brand:"7Artisans",    model:"50mm f1.8",               mtf:7, kg:0.2, price:100,  mark:1, markOis:1, top:false},
    {brand:"Fujifilm",     model:"xf 50mm f/2.0",           mtf:9, kg:0.2, price:500,  sweetSpot:"f/4", mark:1, markOis:1, top:false},
    {brand:"Meike",        model:"50mm f2",                 mtf:6, kg:0.2, price:150,  mark:1, markOis:1, top:false},
    {brand:"Meyer Optik",  model:"Primoplan 58mm f1.9",     mtf:8, kg:0.2, price:1300, mark:1, markOis:1, top:false},
    {brand:"Meyer Optik",  model:"Primoplan 75mm f1.9",     mtf:8, kg:0.3, price:2000, mark:1, markOis:1, top:false},
    {brand:"Opteka",       model:"50mm f2",                 mtf:6, kg:0.2, price:100,  mark:1, markOis:1, top:false},
    {brand:"Handevision",  model:"IBERIT 35mm f2.4",        mtf:6, kg:0.3, price:600, mark:1, markOis:1, top:false},
    {brand:"Lensbaby",     model:"Composer II Sweet 35 f2.5",mtf:7,kg:0.2, price:360,  mark:1, markOis:1, top:false},
    {brand:"Meike",        model:"28mm f2.8",               mtf:7, kg:0.1, price:100,  mark:1, markOis:1, top:false},
    {brand:"Opteka",       model:"28mm f2.8",               mtf:7, kg:0.1, price:100,  mark:1, markOis:1, top:false},
    {brand:"Fujifilm",     model:"xf 27mm f/2.8",           mtf:7, kg:0.1, price:460,  sweetSpot:"f/5.6", mark:1, markOis:1, top:false},
    {brand:"Fujifilm",     model:"xf 18-135mm f/3.5-5.6 OIS",mtf:6,kg:0.5, price:800, sweetSpot:"f/8", mark:1, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xc 15-45mm f/3.5-5.6 OIS",mtf:6,kg:0.1, price:310,  mark:1, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xc 16-50mm f/3.5-5.6 OIS",mtf:6,kg:0.2, price:310,  mark:1, markOis:3, top:false},
    {brand:"Samyang",      model:"Tilt/Shift 24mm f/3.5",   mtf:9, kg:0.8, price:1000, mark:1, markOis:1, top:false},
    // GF lenses
    {brand:"Fujifilm",     model:"gf 55mm f/1.7 R WR",      mtf:9, kg:0.62, price:1450, sweetSpot:"f/5.6", mark:5, markOis:5, top:true},
    {brand:"Fujifilm",     model:"gf 63mm f/2.8 R WR",      mtf:9, kg:0.405,price:1000, sweetSpot:"f/5.6", mark:4, markOis:4, top:true},
    {brand:"Fujifilm",     model:"gf 45mm f/2.8 R WR",      mtf:9, kg:0.49, price:1100, sweetSpot:"f/8", mark:4, markOis:4, top:false},
    {brand:"Fujifilm",     model:"gf 80mm f/1.7 R WR",      mtf:9, kg:0.795,price:1300, sweetSpot:"f/5.6", mark:4, markOis:4, top:false},
    {brand:"Fujifilm",     model:"gf 35-70mm f/4.5-5.6 WR", mtf:8, kg:0.39, price:360,  sweetSpot:"f/8", mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"gf 32-64mm f/4 R LM WR",  mtf:9, kg:0.875,price:1300, sweetSpot:"f/8", mark:3, markOis:3, top:false},
  ],
  Travel: [
    {brand:"Meike",        model:"25mm f0.95",              mtf:7, kg:0.6, price:600, mark:5, markOis:5, top:false},
    {brand:"7Artisans",    model:"35mm f1.2",               mtf:6, kg:0.2, price:150,  mark:4, markOis:4, top:false},
    {brand:"Mitakon",      model:"35mm f0.95 Mk II",        mtf:6, kg:0.6, price:600, mark:4, markOis:4, top:false},
    {brand:"Samyang",      model:"35mm f/1.2",              mtf:7, kg:0.4, price:410,  mark:4, markOis:4, top:true},
    {brand:"Samyang",      model:"21mm F1.4",               mtf:7, kg:0.3, price:410,  mark:4, markOis:4, top:true},
    {brand:"Samyang",      model:"24mm f/1.4",              mtf:6, kg:0.6, price:650, mark:4, markOis:4, top:false},
    {brand:"Fujifilm",     model:"xf 16mm f/1.4",           mtf:8, kg:0.4, price:1000, sweetSpot:"f/4", mark:4, markOis:4, top:true},
    {brand:"Fujifilm",     model:"xf 23mm f/1.4",           mtf:8, kg:0.3, price:950, sweetSpot:"f/4", mark:4, markOis:4, top:true},
    {brand:"7Artisans",    model:"25mm f1.8",               mtf:5, kg:0.2, price:100,  mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xf 56mm f/1.2",           mtf:8, kg:0.4, price:900, sweetSpot:"f/5.6", sweetSpot:"f/5.6", mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xf 35mm f/1.4",           mtf:7, kg:0.2, price:600, sweetSpot:"f/4", mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xf 18mm f/2.0",           mtf:7, kg:0.1, price:550, sweetSpot:"f/5.6", mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xf 23mm f/2.0",           mtf:8, kg:0.2, price:500, sweetSpot:"f/5.6", mark:3, markOis:3, top:false},
    {brand:"Jaray",        model:"35mm F1.6 ii",            mtf:0, kg:0.2, price:100,  mark:3, markOis:3, top:false},
    {brand:"Jaray",        model:"12mm f2.8",               mtf:0, kg:0.4, price:310,  mark:3, markOis:3, top:false},
    {brand:"Kamlan",       model:"50mm f1.1",               mtf:7, kg:0.3, price:200,  mark:3, markOis:3, top:false},
    {brand:"Kamlan",       model:"28mm f1.4",               mtf:6, kg:0.4, price:200,  mark:3, markOis:3, top:false},
    {brand:"Meike",        model:"25mm f1.8",               mtf:7, kg:0.2, price:100,  mark:3, markOis:3, top:false},
    {brand:"Sainsonic",    model:"22mm F1.8",               mtf:0, kg:0.2, price:150,  mark:3, markOis:3, top:false},
    {brand:"Sainsonic",    model:"25mm f1.8",               mtf:0, kg:0.2, price:100,  mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"50mm f/1.2",              mtf:8, kg:0.4, price:430,  mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"35mm f/1.4",              mtf:9, kg:0.7, price:500, mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"16mm f/2",                mtf:8, kg:0.6, price:460,  mark:3, markOis:3, top:false},
    {brand:"Samyang",      model:"20mm f/1.8",              mtf:7, kg:0.5, price:490,  mark:3, markOis:3, top:false},
    {brand:"7Artisans",    model:"55mm f1.4",               mtf:7, kg:0.3, price:100,  mark:2, markOis:2, top:false},
    {brand:"Carl Zeiss",   model:"Touit 32 mm f/1.8",       mtf:7, kg:0.2, price:600, mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 35mm f/2.0",           mtf:7, kg:0.2, price:460,  sweetSpot:"f/4", mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 14mm f/2.8",           mtf:8, kg:0.2, price:950, sweetSpot:"f/4", mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 16-55mm f/2.8",        mtf:8, kg:0.7, price:1200, sweetSpot:"f/8", mark:2, markOis:2, top:false},
    {brand:"Fujifilm",     model:"xf 18-55mm f/2.8-4.0 OIS",mtf:7, kg:0.3, price:750, sweetSpot:"f/8", mark:2, markOis:4, top:true},
    {brand:"Fujifilm",     model:"xf 8-16mm f/2.8",         mtf:9, kg:0.8, price:2000, sweetSpot:"f/5.6", mark:2, markOis:4, top:false},
    {brand:"Fujifilm",     model:"xf 10-24mm f/4 R OIS WR",      mtf:8, kg:0.4, price:1000, sweetSpot:"f/8", mark:2, markOis:4, top:true},
    {brand:"Fujifilm",     model:"xf 10-24mm f/4 R OIS",         mtf:8, kg:0.4, price:410,  sweetSpot:"f/8", mark:2, markOis:4, top:false, est:true},
    {brand:"Handevision",  model:"IBERIT 24mm f2.4",        mtf:7, kg:0.5, price:600, mark:2, markOis:2, top:false},
    {brand:"Lensbaby",     model:"Velvet 56 f1.6 Macro",    mtf:6, kg:0.4, price:410,  mark:2, markOis:2, top:false},
    {brand:"Meike",        model:"35mm f1.7",               mtf:6, kg:0.2, price:100,  mark:2, markOis:2, top:false},
    {brand:"Mitakon",      model:"20mm f2.4 4.5x Macro",    mtf:6, kg:0.2, price:200,  mark:2, markOis:2, top:false},
    {brand:"Sainsonic",    model:"50mm F1.4",               mtf:0, kg:0.2, price:150,  mark:2, markOis:2, top:false},
    {brand:"Sainsonic",    model:"35mm F1.8",               mtf:0, kg:0.2, price:150,  mark:2, markOis:2, top:false},
    {brand:"Samyang",      model:"50mm f/1.4",              mtf:7, kg:0.5, price:410,  mark:2, markOis:2, top:false},
    {brand:"Samyang",      model:"14mm f/2.8",              mtf:7, kg:0.6, price:410,  mark:2, markOis:2, top:false},
    {brand:"7Artisans",    model:"50mm f1.8",               mtf:7, kg:0.2, price:100,  mark:1, markOis:1, top:false},
    {brand:"Fujifilm",     model:"xf 50mm f/2.0",           mtf:9, kg:0.2, price:500,  sweetSpot:"f/4", mark:1, markOis:1, top:false},
    {brand:"Fujifilm",     model:"xf 27mm f/2.8",           mtf:7, kg:0.1, price:460,  sweetSpot:"f/5.6", mark:1, markOis:1, top:false},
    {brand:"Fujifilm",     model:"xf 18-135mm f/3.5-5.6 OIS",mtf:6,kg:0.5, price:800, sweetSpot:"f/8", mark:1, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xc 15-45mm f/3.5-5.6 OIS",mtf:6,kg:0.1, price:310,  mark:1, markOis:3, top:false},
    {brand:"Fujifilm",     model:"xc 16-50mm f/3.5-5.6 OIS",mtf:6,kg:0.2, price:310,  mark:1, markOis:3, top:false},
    {brand:"Handevision",  model:"IBERIT 35mm f2.4",        mtf:6, kg:0.3, price:600, mark:1, markOis:1, top:false},
    {brand:"Jaray",        model:"14mm F3.5",               mtf:0, kg:0.2, price:200,  mark:1, markOis:1, top:false},
    {brand:"Lensbaby",     model:"Composer II Sweet 35 f2.5",mtf:7,kg:0.2, price:360,  mark:1, markOis:1, top:false},
    {brand:"Meyer Optik",  model:"Primoplan 58mm f1.9",     mtf:8, kg:0.2, price:1300, mark:1, markOis:1, top:false},
    {brand:"Meyer Optik",  model:"Primoplan 75mm f1.9",     mtf:8, kg:0.3, price:2000, mark:1, markOis:1, top:false},
    {brand:"Meike",        model:"28mm f2.8",               mtf:7, kg:0.1, price:100,  mark:1, markOis:1, top:false},
    {brand:"Opteka",       model:"28mm f2.8",               mtf:7, kg:0.1, price:100,  mark:1, markOis:1, top:false},
    {brand:"Opteka",       model:"50mm f2",                 mtf:6, kg:0.2, price:100,  mark:1, markOis:1, top:false},
    {brand:"Samyang",      model:"Tilt/Shift 24mm f/3.5",   mtf:9, kg:0.8, price:1000, mark:1, markOis:1, top:false},
    {brand:"7Artisans",    model:"35mm f2",                 mtf:5, kg:0.3, price:200,  mark:2, markOis:2, top:false},
    // GF lenses
    {brand:"Fujifilm",     model:"gf 35-70mm f/4.5-5.6 WR", mtf:8, kg:0.39, price:360,  sweetSpot:"f/8", mark:5, markOis:5, top:true},
    {brand:"Fujifilm",     model:"gf 50mm f/3.5 R LM WR",   mtf:9, kg:0.335,price:410,  sweetSpot:"f/8", mark:4, markOis:4, top:true},
    {brand:"Fujifilm",     model:"gf 63mm f/2.8 R WR",      mtf:9, kg:0.405,price:1000, sweetSpot:"f/5.6", mark:4, markOis:4, top:false},
    {brand:"Fujifilm",     model:"gf 32-64mm f/4 R LM WR",  mtf:9, kg:0.875,price:1300, sweetSpot:"f/8", mark:4, markOis:4, top:false},
    {brand:"Fujifilm",     model:"gf 45mm f/2.8 R WR",      mtf:9, kg:0.49, price:1100, sweetSpot:"f/8", mark:3, markOis:3, top:false},
    {brand:"Fujifilm",     model:"gf 55mm f/1.7 R WR",      mtf:9, kg:0.62, price:1450, sweetSpot:"f/5.6", mark:3, markOis:3, top:false},
  ],
  Landscape: [
    {brand:"Fujifilm",    model:"xf 14mm f/2.8",            mtf:8, kg:0.2, price:950, sweetSpot:"f/4", mark:null, top:true},
    {brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS WR",       mtf:8, kg:0.4, price:1000, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS",          mtf:8, kg:0.4, price:410,  sweetSpot:"f/8", mark:null, top:false, est:true},
    {brand:"Fujifilm",    model:"xf 8-16mm f/2.8 WR",            mtf:9, kg:0.8, price:2000, mark:null, top:true},
    {brand:"Fujifilm",    model:"xf 100-400mm f/4.5-5.6 OIS",mtf:8,kg:1.4, price:1850, sweetSpot:"f/8", mark:4, top:true},
    {brand:"Samyang",     model:"16mm f/2",                 mtf:8, kg:0.6, price:460,  mark:null, top:true},
    {brand:"Samyang",     model:"135mm f/2",                mtf:9, kg:0.8, price:550, mark:null, top:true},
    {brand:"7Artisans",   model:"7.5mm F2.8",               mtf:6, kg:0.3, price:200,  mark:null, top:false},
    {brand:"Carl Zeiss",  model:"Touit 12 mm f/2.8",        mtf:8, kg:0.3, price:900, mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 16-55mm f/2.8",         mtf:8, kg:0.7, price:1200, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 18mm f/1.4 LM WR",         mtf:9, kg:0.4, price:1100, sweetSpot:"f/2.8", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 16mm f/2.8 WR LM",         mtf:8, kg:0.1, price:310,  sweetSpot:"f/4", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 33mm f/1.4 LM WR",         mtf:9, kg:0.4, price:850,  sweetSpot:"f/4", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 27mm f/2.8 WR",            mtf:8, kg:0.1, price:260,  mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 8-16mm f/2.8",          mtf:9, kg:0.8, price:2000, sweetSpot:"f/5.6", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 18-55mm f/2.8-4.0 OIS", mtf:7, kg:0.3, price:750, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 18-135mm f/3.5-5.6 OIS",mtf:6, kg:0.5, price:800, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"xc 15-45mm f/3.5-5.6 OIS", mtf:6, kg:0.1, price:310,  mark:null, top:false},
    {brand:"Fujifilm",    model:"xc 16-50mm f/3.5-5.6 OIS", mtf:6, kg:0.2, price:310,  mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 200mm f/2.0",           mtf:10,kg:2.3, price:6000, sweetSpot:"f/4", mark:5, top:false},
    {brand:"Fujifilm",    model:"xf 80mm f/2.8 Macro",      mtf:9, kg:0.8, price:1350, sweetSpot:"f/4", mark:4, top:false},
    {brand:"Handevision", model:"IBERIT 24mm f2.4",         mtf:7, kg:0.5, price:600, mark:null, top:false},
    {brand:"Lensbaby",    model:"5.8mm Circular Fisheye",   mtf:7, kg:0.3, price:200,  mark:null, top:false},
    {brand:"Meike",       model:"12mm f2.8",                mtf:6, kg:0.4, price:260,  mark:null, top:false},
    {brand:"Meike",       model:"6.5mm Fisheye f2.0",       mtf:8, kg:0.3, price:150,  mark:null, top:false},
    {brand:"Meike",       model:"8mm Fisheye f3.5",         mtf:7, kg:0.5, price:200,  mark:null, top:false},
    {brand:"Meike",       model:"85mm f2.8 Macro",          mtf:8, kg:0.5, price:310,  mark:null, top:false},
    {brand:"Mitakon",     model:"20mm f2.4 4.5x Macro",     mtf:7, kg:0.2, price:200,  mark:null, top:false},
    {brand:"Opteka",      model:"12mm f2.8",                mtf:6, kg:0.4, price:260,  mark:null, top:false},
    {brand:"Opteka",      model:"6.5mm f2 Fisheye",         mtf:8, kg:0.3, price:150,  mark:null, top:false},
    {brand:"Samyang",     model:"10mm f/2.8",               mtf:7, kg:0.6, price:500, mark:null, top:false},
    {brand:"Samyang",     model:"12mm f/2",                 mtf:8, kg:0.3, price:410,  mark:null, top:false},
    {brand:"Samyang",     model:"12mm f/2.8",               mtf:7, kg:0.5, price:500, mark:null, top:false},
    {brand:"Samyang",     model:"14mm f/2.8",               mtf:7, kg:0.6, price:410,  mark:null, top:false},
    {brand:"Samyang",     model:"20mm f/1.8",               mtf:7, kg:0.5, price:490,  mark:null, top:false},
    {brand:"Samyang",     model:"21mm F1.4",                mtf:7, kg:0.3, price:410,  mark:null, top:false},
    {brand:"Samyang",     model:"24mm f/1.4",               mtf:6, kg:0.6, price:650, mark:null, top:false},
    {brand:"Samyang",     model:"8mm f/2.8",                mtf:7, kg:0.2, price:330,  mark:null, top:false},
    {brand:"Samyang",     model:"8mm f/3.5",                mtf:8, kg:0.4, price:330,  mark:null, top:false},
    {brand:"Samyang",     model:"Tilt/Shift 24mm f/3.5",    mtf:9, kg:0.8, price:1000, mark:null, top:false},
    {brand:"Samyang",     model:"85mm f/1.4",               mtf:8, kg:0.5, price:360,  mark:null, top:false},
    {brand:"Samyang",     model:"300mm f/6.3",              mtf:5, kg:0.4, price:310,  mark:null, top:false},
    {brand:"Venus Laowa", model:"9mm f2.8 ZeroD",           mtf:8, kg:0.2, price:500, mark:null, top:false},
    {brand:"Meyer Optik", model:"Trioplan 100mm 2.8",       mtf:7, kg:0.8, price:1650, mark:1, top:false},
    {brand:"Samyang",     model:"100mm f/2.8",              mtf:6, kg:0.7, price:500, mark:null, top:false},
    {brand:"Handevision", model:"IBERIT 90mm f/2.4",        mtf:7, kg:0.4, price:500, mark:1, top:false},
    {brand:"Lensbaby",    model:"Composer II Sweet 80 f2.8",mtf:7, kg:0.2, price:410,  mark:null, top:false},
    {brand:"Lensbaby",    model:"Velvet 85mm f1.8",         mtf:6, kg:0.5, price:460,  mark:null, top:false},
    {brand:"Samyang",     model:"85mm f/1.4",               mtf:8, kg:0.5, price:360,  mark:null, top:false},
    {brand:"Samyang",     model:"85mm f/1.8",               mtf:8, kg:0.4, price:410,  mark:null, top:false},
    // GF lenses
    {brand:"Fujifilm",    model:"gf 23mm f/4 R LM WR",      mtf:9, kg:0.845,price:1400, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 20-35mm f/4 R WR",      mtf:9, kg:0.525,price:1400, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 30mm f/3.5 R WR",       mtf:9, kg:0.51, price:850, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 32-64mm f/4 R LM WR",   mtf:9, kg:0.875,price:1300, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"gf 45-100mm f/4 R LM OIS WR", mtf:9, kg:1.14, price:1450, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"gf 100-200mm f/5.6 R LM OIS WR",mtf:9,kg:1.055,price:1650,sweetSpot:"f/8", mark:null,top:false},
  ],
  Architecture: [
    {brand:"Fujifilm",    model:"xf 14mm f/2.8",            mtf:8, kg:0.2, price:950, sweetSpot:"f/4", mark:null, top:true},
    {brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS WR",       mtf:8, kg:0.4, price:1000, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"xf 10-24mm f/4 R OIS",          mtf:8, kg:0.4, price:410,  sweetSpot:"f/8", mark:null, top:false, est:true},
    {brand:"Meike",       model:"6.5mm Fisheye f2.0",       mtf:8, kg:0.3, price:150,  mark:null, top:true},
    {brand:"Samyang",     model:"12mm f/2",                 mtf:8, kg:0.3, price:410,  mark:null, top:true},
    {brand:"Samyang",     model:"16mm f/2",                 mtf:8, kg:0.6, price:460,  mark:null, top:true},
    {brand:"Samyang",     model:"Tilt/Shift 24mm f/3.5",    mtf:9, kg:0.8, price:1000, mark:null, top:true},
    {brand:"7Artisans",   model:"7.5mm F2.8",               mtf:6, kg:0.3, price:200,  mark:null, top:false},
    {brand:"Carl Zeiss",  model:"Touit 12 mm f/2.8",        mtf:8, kg:0.3, price:900, mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 16-55mm f/2.8",         mtf:8, kg:0.7, price:1200, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 18mm f/1.4 LM WR",         mtf:9, kg:0.4, price:1100, sweetSpot:"f/2.8", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 16mm f/2.8 WR LM",         mtf:8, kg:0.1, price:310,  sweetSpot:"f/4", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 33mm f/1.4 LM WR",         mtf:9, kg:0.4, price:850,  sweetSpot:"f/4", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 27mm f/2.8 WR",            mtf:8, kg:0.1, price:260,  mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 8-16mm f/2.8",          mtf:9, kg:0.8, price:2000, sweetSpot:"f/5.6", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 18-55mm f/2.8-4.0 OIS", mtf:7, kg:0.3, price:750, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"xf 18-135mm f/3.5-5.6 OIS",mtf:6, kg:0.5, price:800, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"xc 15-45mm f/3.5-5.6 OIS", mtf:6, kg:0.1, price:310,  mark:null, top:false},
    {brand:"Fujifilm",    model:"xc 16-50mm f/3.5-5.6 OIS", mtf:6, kg:0.2, price:310,  mark:null, top:false},
    {brand:"Handevision", model:"IBERIT 24mm f2.4",         mtf:7, kg:0.5, price:600, mark:null, top:false},
    {brand:"Lensbaby",    model:"5.8mm Circular Fisheye",   mtf:7, kg:0.3, price:200,  mark:null, top:false},
    {brand:"Meike",       model:"12mm f2.8",                mtf:6, kg:0.4, price:260,  mark:null, top:false},
    {brand:"Meike",       model:"8mm Fisheye f3.5",         mtf:7, kg:0.5, price:200,  mark:null, top:false},
    {brand:"Mitakon",     model:"20mm f2.4 4.5x Macro",     mtf:7, kg:0.2, price:200,  mark:null, top:false},
    {brand:"Opteka",      model:"12mm f2.8",                mtf:6, kg:0.4, price:260,  mark:null, top:false},
    {brand:"Opteka",      model:"6.5mm f2 Fisheye",         mtf:8, kg:0.3, price:150,  mark:null, top:false},
    {brand:"Samyang",     model:"10mm f/2.8",               mtf:7, kg:0.6, price:500, mark:null, top:false},
    {brand:"Samyang",     model:"12mm f/2.8",               mtf:7, kg:0.5, price:500, mark:null, top:false},
    {brand:"Samyang",     model:"14mm f/2.8",               mtf:7, kg:0.6, price:410,  mark:null, top:false},
    {brand:"Samyang",     model:"20mm f/1.8",               mtf:7, kg:0.5, price:490,  mark:null, top:false},
    {brand:"Samyang",     model:"21mm F1.4",                mtf:7, kg:0.3, price:410,  mark:null, top:false},
    {brand:"Samyang",     model:"24mm f/1.4",               mtf:6, kg:0.6, price:650, mark:null, top:false},
    {brand:"Samyang",     model:"8mm f/2.8",                mtf:7, kg:0.2, price:330,  mark:null, top:false},
    {brand:"Samyang",     model:"8mm f/3.5",                mtf:8, kg:0.4, price:330,  mark:null, top:false},
    {brand:"Venus Laowa", model:"9mm f2.8 ZeroD",           mtf:8, kg:0.2, price:500, mark:null, top:false},
    // GF lenses
    {brand:"Fujifilm",    model:"gf 23mm f/4 R LM WR",      mtf:9, kg:0.845,price:1400, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 20-35mm f/4 R WR",      mtf:9, kg:0.525,price:1400, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 30mm f/3.5 R WR",       mtf:9, kg:0.51, price:850, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 30mm f/5.6 T/S",        mtf:9, kg:0.88, price:1800, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 110mm f/5.6 T/S Macro", mtf:9, kg:1.05, price:2000, sweetSpot:"f/8", sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 32-64mm f/4 R LM WR",   mtf:9, kg:0.875,price:1300, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"gf 45-100mm f/4 R LM OIS WR", mtf:9, kg:1.14, price:1450, sweetSpot:"f/8", mark:null, top:false},
  ],
  Portrait: [
    {brand:"Fujifilm",    model:"xf 16mm f/1.4",               mtf:8, kg:0.4, price:1000, sweetSpot:"f/4", mark:3, top:true},
    {brand:"Fujifilm",    model:"xf 23mm f/2.0",               mtf:8, kg:0.2, price:500,  sweetSpot:"f/5.6", mark:3, top:true},
    {brand:"Fujifilm",    model:"xf 35mm f/1.4",               mtf:7, kg:0.2, price:600,  sweetSpot:"f/4", mark:3, top:true},
    {brand:"Fujifilm",    model:"xf 50mm f/2.0",               mtf:9, kg:0.2, price:500,  sweetSpot:"f/4", mark:4, top:true},
    {brand:"Fujifilm",    model:"xf 56mm f/1.2",               mtf:8, kg:0.4, price:900,  sweetSpot:"f/5.6", sweetSpot:"f/5.6", mark:4, top:true},
    {brand:"Fujifilm",    model:"xf 90mm f/2.0",               mtf:9, kg:0.5, price:800,  sweetSpot:"f/2.8", mark:5, top:true},
    {brand:"Carl Zeiss",  model:"Touit 32 mm f/1.8",           mtf:7, kg:0.2, price:600,  mark:3, top:false},
    {brand:"Fujifilm",    model:"xf 18mm f/2.0",               mtf:7, kg:0.1, price:550,  sweetSpot:"f/5.6", mark:2, top:false},
    {brand:"Fujifilm",    model:"xf 23mm f/1.4",               mtf:8, kg:0.3, price:950,  sweetSpot:"f/4", mark:3, top:false},
    {brand:"Fujifilm",    model:"xf 35mm f/2.0",               mtf:7, kg:0.2, price:460,  sweetSpot:"f/4", mark:3, top:false},
    // GF lenses
    {brand:"Fujifilm",    model:"gf 80mm f/1.7 R WR",          mtf:9, kg:0.795,price:1300, sweetSpot:"f/5.6", mark:5, top:true},
    {brand:"Fujifilm",    model:"gf 110mm f/2 R LM WR",        mtf:10,kg:1.0,  price:1850, sweetSpot:"f/5.6", mark:5, top:true},
    {brand:"Fujifilm",    model:"gf 55mm f/1.7 R WR",          mtf:9, kg:0.62, price:1450, sweetSpot:"f/5.6", mark:4, top:true},
    {brand:"Fujifilm",    model:"gf 63mm f/2.8 R WR",          mtf:9, kg:0.405,price:1000, sweetSpot:"f/5.6", mark:4, top:false},
    {brand:"Fujifilm",    model:"gf 45mm f/2.8 R WR",          mtf:9, kg:0.49, price:1100, sweetSpot:"f/8", mark:3, top:false},
    {brand:"Fujifilm",    model:"gf 250mm f/4 R LM OIS WR",    mtf:9, kg:1.535,price:2300, sweetSpot:"f/8", mark:4, top:false},
  ],
  Sport: [
    {brand:"Fujifilm",    model:"xf 80mm f/2.8 Macro",      mtf:9, kg:0.8, price:1350, sweetSpot:"f/4", mark:4, top:true},
    {brand:"Fujifilm",    model:"xf 90mm f/2.0",               mtf:9, kg:0.5, price:800,  sweetSpot:"f/2.8", mark:3, top:true},
    {brand:"Fujifilm",    model:"xf 50-140mm f/2.8 OIS",    mtf:8, kg:1.0, price:1600, mark:4, top:true},
    {brand:"Fujifilm",    model:"xf 55-200mm f/3.5-4.8 OIS",mtf:7, kg:0.6, price:700, sweetSpot:"f/8", mark:3, top:true},
    {brand:"Fujifilm",    model:"xf 100-400mm f/4.5-5.6 OIS",mtf:8,kg:1.4, price:1850, sweetSpot:"f/8", mark:4, top:true},
    {brand:"Fujifilm",    model:"xc 50-230mm f/4.5-6.7 OIS",mtf:6, kg:0.4, price:410,  mark:2, top:true},
    {brand:"7Artisans",   model:"50mm f1.8",                mtf:7, kg:0.2, price:100,  mark:null, top:false},
    {brand:"7Artisans",   model:"55mm f1.4",                mtf:7, kg:0.3, price:100,  mark:null, top:false},
    {brand:"Carl Zeiss",  model:"Touit 50 mm f/2.8",        mtf:8, kg:0.3, price:850, mark:1, top:false},
    {brand:"Fujifilm",    model:"xf 200mm f/2.0",           mtf:10,kg:2.3, price:6000,sweetSpot:"f/4", mark:5, top:false},
    {brand:"Fujifilm",    model:"xf 50mm f/2.0",               mtf:9, kg:0.2, price:500,  sweetSpot:"f/4", mark:1, top:false},
    {brand:"Fujifilm",    model:"xf 56mm f/1.2",               mtf:8, kg:0.4, price:900,  sweetSpot:"f/5.6", sweetSpot:"f/5.6", mark:1, top:false},
    {brand:"Fujifilm",    model:"xf 60mm f/2.4 Macro",      mtf:8, kg:0.2, price:700, mark:1, top:false},
    {brand:"Handevision", model:"IBERIT 50mm f2.4",         mtf:7, kg:0.3, price:600, mark:1, top:false},
    {brand:"Handevision", model:"IBERIT 75mm f2.4",         mtf:7, kg:0.3, price:600, mark:1, top:false},
    {brand:"Handevision", model:"IBERIT 90mm f/2.4",        mtf:7, kg:0.4, price:500, mark:1, top:false},
    {brand:"Kamlan",      model:"50mm f1.1",                mtf:7, kg:0.3, price:200,  mark:null, top:false},
    {brand:"Meike",       model:"50mm f2",                  mtf:6, kg:0.2, price:150,  mark:null, top:false},
    {brand:"Meike",       model:"85mm f2.8 Macro",          mtf:8, kg:0.5, price:310,  mark:null, top:false},
    {brand:"Meyer Optik", model:"Primoplan 58mm f1.9",      mtf:8, kg:0.2, price:1300, mark:1, top:false},
    {brand:"Meyer Optik", model:"Primoplan 75mm f1.9",      mtf:8, kg:0.3, price:2000, mark:1, top:false},
    {brand:"Meyer Optik", model:"Trioplan 100mm 2.8",       mtf:7, kg:0.8, price:1650, mark:1, top:false},
    {brand:"Meyer Optik", model:"Trioplan 50mm f/2.9",      mtf:7, kg:0.2, price:1550, mark:1, top:false},
    {brand:"Samyang",     model:"100mm f/2.8",              mtf:6, kg:0.7, price:500, mark:null, top:false},
    {brand:"Samyang",     model:"135mm f/2",                mtf:9, kg:0.8, price:550, mark:null, top:false},
    {brand:"Samyang",     model:"50mm f/1.2",               mtf:8, kg:0.4, price:430,  mark:null, top:false},
    {brand:"Samyang",     model:"50mm f/1.4",               mtf:7, kg:0.5, price:410,  mark:null, top:false},
    {brand:"Samyang",     model:"85mm f/1.4",               mtf:8, kg:0.5, price:360,  mark:null, top:false},
    {brand:"Samyang",     model:"85mm f/1.8",               mtf:8, kg:0.4, price:410,  mark:null, top:false},
    // GF lenses
    {brand:"Fujifilm",    model:"gf 200mm f/2 R LM OIS WR", mtf:10,kg:3.4,  price:4100, sweetSpot:"f/5.6", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 250mm f/4 R LM OIS WR",    mtf:9, kg:1.535,price:2300, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 45-100mm f/4 R LM OIS WR",mtf:9,kg:1.14,price:1450, sweetSpot:"f/8", mark:null, top:false},
    {brand:"Fujifilm",    model:"gf 100-200mm f/5.6 R LM OIS WR",mtf:9,kg:1.055,price:1650,sweetSpot:"f/8", mark:null,top:false},
  ],
  Wildlife: [
    {brand:"Fujifilm",    model:"xf 200mm f/2.0",           mtf:10,kg:2.3, price:6000,sweetSpot:"f/4", mark:5, top:true},
    {brand:"Fujifilm",    model:"xf 200mm f/2.0",              mtf:10,kg:2.3,  price:6000, sweetSpot:"f/4", mark:5, top:true},
    {brand:"Fujifilm",    model:"xf 50-140mm f/2.8 OIS",    mtf:8, kg:1.0, price:1600, mark:4, top:true},
    {brand:"Fujifilm",    model:"xf 55-200mm f/3.5-4.8 OIS",mtf:7, kg:0.6, price:700, sweetSpot:"f/8", mark:3, top:true},
    {brand:"Fujifilm",    model:"xf 100-400mm f/4.5-5.6 OIS",mtf:8,kg:1.4, price:1850, sweetSpot:"f/8", mark:4, top:true},
    {brand:"Samyang",     model:"135mm f/2",                mtf:9, kg:0.8, price:550, mark:null, top:true},
    {brand:"7Artisans",   model:"50mm f1.8",                mtf:7, kg:0.2, price:100,  mark:null, top:false},
    {brand:"7Artisans",   model:"55mm f1.4",                mtf:7, kg:0.3, price:100,  mark:null, top:false},
    {brand:"Carl Zeiss",  model:"Touit 50 mm f/2.8",        mtf:8, kg:0.3, price:850, mark:1, top:false},
    {brand:"Fujifilm",    model:"xf 90mm f/2.0",               mtf:9, kg:0.5, price:800,  sweetSpot:"f/2.8", mark:3, top:false},
    {brand:"Fujifilm",    model:"xf 80mm f/2.8 Macro",         mtf:9, kg:0.8, price:1350, sweetSpot:"f/4", mark:4, top:false},
    {brand:"Fujifilm",    model:"xf 60mm f/2.4 Macro",      mtf:8, kg:0.2, price:700, mark:1, top:false},
    {brand:"Fujifilm",    model:"xf 80mm f/2.8 Macro",      mtf:9, kg:0.8, price:1350, sweetSpot:"f/4", mark:4, top:false},
    {brand:"Fujifilm",    model:"xc 50-230mm f/4.5-6.7 OIS",mtf:6, kg:0.4, price:410,  mark:2, top:false},
    {brand:"Handevision", model:"IBERIT 50mm f2.4",         mtf:7, kg:0.3, price:600, mark:1, top:false},
    {brand:"Handevision", model:"IBERIT 75mm f2.4",         mtf:7, kg:0.3, price:600, mark:1, top:false},
    {brand:"Handevision", model:"IBERIT 90mm f/2.4",        mtf:7, kg:0.4, price:500, mark:1, top:false},
    {brand:"Kamlan",      model:"50mm f1.1",                mtf:7, kg:0.3, price:200,  mark:null, top:false},
    {brand:"Meike",       model:"50mm f2",                  mtf:6, kg:0.2, price:150,  mark:null, top:false},
    {brand:"Meike",       model:"85mm f2.8 Macro",          mtf:8, kg:0.5, price:310,  mark:null, top:false},
    {brand:"Meyer Optik", model:"Primoplan 58mm f1.9",      mtf:8, kg:0.2, price:1300, mark:1, top:false},
    {brand:"Meyer Optik", model:"Primoplan 75mm f1.9",      mtf:8, kg:0.3, price:2000, mark:1, top:false},
    {brand:"Meyer Optik", model:"Trioplan 100mm 2.8",       mtf:7, kg:0.8, price:1650, mark:1, top:false},
    {brand:"Samyang",     model:"100mm f/2.8",              mtf:6, kg:0.7, price:500, mark:null, top:false},
    {brand:"Samyang",     model:"50mm f/1.2",               mtf:8, kg:0.4, price:430,  mark:null, top:false},
    {brand:"Samyang",     model:"85mm f/1.4",               mtf:8, kg:0.5, price:360,  mark:null, top:false},
    {brand:"Samyang",     model:"85mm f/1.8",               mtf:8, kg:0.4, price:410,  mark:null, top:false},
    // GF lenses
    {brand:"Fujifilm",    model:"gf 500mm f/5.6 R LM OIS WR",mtf:9,kg:2.1,  price:3600, sweetSpot:"f/8", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 200mm f/2 R LM OIS WR", mtf:10,kg:3.4,  price:4100, sweetSpot:"f/5.6", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 200mm f/2 R LM OIS WR",    mtf:10,kg:3.4,  price:4100, sweetSpot:"f/5.6", mark:null, top:true},
    {brand:"Fujifilm",    model:"gf 100-200mm f/5.6 R LM OIS WR",mtf:9,kg:1.055,price:1650,sweetSpot:"f/8", mark:null,top:false},
    {brand:"Fujifilm",    model:"gf 45-100mm f/4 R LM OIS WR",mtf:9,kg:1.14,price:1450, sweetSpot:"f/8", mark:null, top:false},
  ],
};

// ─── STYLES ───────────────────────────────────────────────────────────────────

const css = `
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0a0a0a;
    color: #e0d8cc;
    font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 14px;
    min-height: 100vh;
  }

  .app {
    max-width: 1100px;
    margin: 0 auto;
    padding: 20px 16px 40px;
  }

  .header {
    border-bottom: 1px solid #2a2520;
    padding-bottom: 14px;
    margin-bottom: 20px;
    display: flex;
    align-items: baseline;
    gap: 16px;
  }

  .header h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 17px;
    font-weight: 600;
    color: #e8a045;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  .header .sub {
    font-size: 11px;
    color: #b0a898;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .tabs {
    display: flex;
    gap: 2px;
    margin-bottom: 20px;
    border-bottom: 1px solid #1e1b16;
  }

  .tab {
    background: none;
    border: none;
    padding: 7px 16px 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #b0a898;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 2px solid transparent;
    transition: all 0.15s;
  }

  .tab:hover { color: #e0d8cc; }
  .tab.active { color: #e8a045; border-bottom-color: #e8a045; }

  /* LENS EXPLORER */
  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
    align-items: center;
  }

  .filter-group {
    display: flex;
    gap: 3px;
    align-items: center;
  }

  .filter-label {
    font-size: 11px;
    color: #b0a898;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-right: 4px;
    white-space: nowrap;
  }

  .chip {
    background: #141210;
    border: 1px solid #2a2520;
    color: #a09888;
    padding: 3px 9px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.12s;
    white-space: nowrap;
  }

  .chip:hover { border-color: #b0a898; color: #e0d8cc; }
  .chip.on { background: #1e1710; border-color: #e8a045; color: #e8a045; }

  .search-box {
    background: #141210;
    border: 1px solid #2a2520;
    color: #e0d8cc;
    padding: 4px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    width: 160px;
    outline: none;
  }

  .search-box:focus { border-color: #b0a898; }
  .search-box::placeholder { color: #4a4540; }

  .sort-select {
    background: #141210;
    border: 1px solid #2a2520;
    color: #a09888;
    padding: 4px 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    outline: none;
    cursor: pointer;
  }

  .count-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #8a8070;
    margin-left: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
  }

  thead th {
    background: #0f0d0b;
    color: #b0a898;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 7px 8px;
    text-align: left;
    font-size: 11px;
    border-bottom: 1px solid #2a2520;
    white-space: nowrap;
  }

  thead th.num { text-align: right; }

  tbody tr { border-bottom: 1px solid #181510; transition: background 0.1s; }
  tbody tr:hover { background: #141210; }

  tbody td {
    padding: 6px 8px;
    color: #c0b8a8;
    white-space: nowrap;
  }

  tbody td.num { text-align: right; font-size: 12px; }
  tbody td.brand { color: #b0a898; font-size: 11px; }
  tbody td.model { color: #e0d8cc; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  tbody td.price { color: #e8a045; }

  .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; }
  .dot.yes { background: #5a9060; }
  .dot.no  { background: #1e1b16; }

  .mtf-bar {
    display: inline-flex;
    gap: 1px;
  }
  /* ── Mobile lens cards ── */
  .lens-cards { display:flex; flex-direction:column; gap:8px; }
  .lens-card {
    background: #111; border: 1px solid #2a2520; border-radius:4px;
    padding: 10px 12px; display:flex; flex-direction:column; gap:6px;
  }
  .lens-card.top { background: #0f0e0b; border-color: #3a3020; }
  .lens-card.filtered { opacity: 0.4; }
  .lens-card-header { display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }
  .lens-card-brand { font-size:10px; color:#8a8070; font-family:'IBM Plex Mono',monospace; text-transform:uppercase; letter-spacing:0.06em; }
  .lens-card-model { font-size:13px; color:#e0d8cc; line-height:1.3; margin-top:1px; }
  .lens-card-mode  { font-size:10px; font-family:'IBM Plex Mono',monospace; font-weight:600; padding:2px 6px; border-radius:2px; white-space:nowrap; flex-shrink:0; }
  .lens-card-row   { display:flex; align-items:center; justify-content:space-between; gap:8px; }
  .lens-card-fl    { font-size:11px; color:#b0a898; font-family:'IBM Plex Mono',monospace; }
  .lens-card-fl span { color:#8a8070; font-size:10px; margin-left:4px; }
  .lens-card-badges { display:flex; gap:4px; }
  .lens-card-badge { font-size:10px; font-family:'IBM Plex Mono',monospace; padding:1px 5px; border-radius:2px; }
  .lens-card-price { font-size:12px; font-family:'IBM Plex Mono',monospace; color:#e0d8cc; }
  .lens-card-mtf   { display:flex; gap:2px; align-items:center; }

  .mtf-pip {
    width: 5px; height: 9px;
    background: #2a2520;
    border: 1px solid #554e44;
  }
  .mtf-pip.filled { background: #e8a045; opacity: 0.8; border-color: #e8a045; }

  .type-badge {
    font-size: 9px;
    padding: 1px 5px;
    background: #1e1b16;
    color: #8a8070;
    letter-spacing: 0.06em;
  }
  .type-badge.Z { background: #1a1a10; color: #a09040; }

  /* CALCULATOR */
  .calc-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 20px;
  }

  .calc-panel {
    background: #0f0d0b;
    border: 1px solid #1e1b16;
    padding: 16px;
  }

  .calc-panel h3 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #b0a898;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e1b16;
  }

  .field {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }

  .field label {
    font-size: 11px;
    color: #b0a898;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    width: 52px;
    flex-shrink: 0;
    text-align: left;
  }

  .field input[type=range] {
    flex: 1;
    accent-color: #e8a045;
    cursor: pointer;
  }

  .field .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #e8a045;
    width: 60px;
    text-align: right;
  }

  .field .unit {
    font-size: 10px;
    color: #8a8070;
    width: 28px;
  }

  .results-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #2a2520;
    margin-top: 16px;
  }

  .result-cell {
    background: #0f0d0b;
    padding: 12px;
    text-align: center;
  }

  .result-cell .r-label {
    font-size: 10px;
    color: #8a8070;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
  }

  .result-cell .r-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 18px;
    font-weight: 600;
    color: #e8a045;
  }

  .result-cell .r-unit {
    font-size: 10px;
    color: #b0a898;
    margin-top: 2px;
  }

  .re-bar-wrap {
    margin: 16px 0 0;
    background: #141210;
    border: 1px solid #1e1b16;
    padding: 14px 16px;
  }

  .re-bar-label {
    font-size: 11px;
    color: #b0a898;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
  }

  .re-bar-track {
    height: 10px;
    background: #2a2520;
    position: relative;
  }

  .re-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #8a5020, #e8a045);
    transition: width 0.3s;
    max-width: 100%;
  }

  /* TRADE */
  .trade-row { cursor: default; }
  .top-deal td.model { color: #e8c070 !important; }
  .ratio-bar-wrap { display: flex; align-items: center; gap: 6px; }
  .ratio-bar { height: 6px; background: #e8a045; opacity: 0.6; max-width: 100px; }
  .priority-badge {
    font-size: 10px;
    padding: 1px 5px;
    background: #1a1510;
    border: 1px solid #7a7060;
    color: #c0a050;
    font-family: 'IBM Plex Mono', monospace;
  }

  /* GENRES */
  .genre-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 18px;
  }

  .genre-btn {
    background: #141210;
    border: 1px solid #2a2520;
    color: #a09888;
    padding: 5px 13px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    transition: all 0.12s;
  }

  .genre-btn:hover { border-color: #b0a898; color: #e0d8cc; }
  .genre-btn.active { background: #1e1710; border-color: #e8a045; color: #e8a045; }

  .top-badge {
    display: inline-block;
    font-size: 9px;
    padding: 1px 5px;
    background: #e8a045;
    color: #0a0a0a;
    font-weight: 600;
    letter-spacing: 0.08em;
    margin-left: 6px;
    vertical-align: middle;
    font-family: 'IBM Plex Mono', monospace;
  }

  .empty { color: #8a8070; font-family: 'IBM Plex Mono', monospace; font-size: 12px; padding: 20px 0; }
`;

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function MtfPips({ val }) {
  if (!val) return <span style={{color:"#8a8070"}}>–</span>;
  return (
    <span className="mtf-bar">
      {[...Array(10)].map((_, i) => (
        <span key={i} className={`mtf-pip${i < val ? " filled" : ""}`} />
      ))}
    </span>
  );
}

function Dot({ yes }) {
  return <span className={`dot ${yes ? "yes" : "no"}`} />;
}

function FilterDropdown({ label, options, selected, onChange, multi = true, defaultValue }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    function handleClick(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false); }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const def = defaultValue !== undefined ? defaultValue : (multi ? null : options[0]?.value ?? null);
  const isActive = multi ? selected.length > 0 : selected !== def;
  const btnLabel = multi
    ? selected.length === 0 ? `${label}: All` : selected.length === 1 ? `${label}: ${options.find(o=>o.value===selected[0])?.label ?? selected[0]}` : `${label}: ${selected.length}`
    : `${label}: ${options.find(o=>o.value===selected)?.label ?? "Any"}`;

  function toggle(val) {
    if (multi) onChange(selected.includes(val) ? selected.filter(x=>x!==val) : [...selected, val]);
    else { onChange(val); setOpen(false); }
  }

  return (
    <div ref={ref} style={{position:"relative", display:"inline-block"}}>
      <button onClick={() => setOpen(o => !o)}
        className={`chip${isActive ? " on" : ""}`}
        style={{padding:"2px 10px", display:"flex", alignItems:"center", gap:6}}>
        <span>{btnLabel}</span>
        <span style={{fontSize:8, opacity:0.6}}>{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div style={{position:"absolute", top:"calc(100% + 4px)", left:0, zIndex:100,
          background:"#1a1814", border:"1px solid #3a3530", borderRadius:4,
          minWidth:160, padding:"4px 0", boxShadow:"0 4px 12px rgba(0,0,0,0.5)"}}>
          {options.map(({label: ol, value: ov}) => {
            const active = multi ? selected.includes(ov) : selected === ov;
            return (
              <label key={ov} onClick={() => toggle(ov)} style={{display:"flex", alignItems:"center", gap:8,
                padding:"5px 12px", cursor:"pointer", fontSize:11,
                fontFamily:"'IBM Plex Mono',monospace",
                color: active ? "#e8a045" : "#b0a898",
                background: active ? "#1e1a10" : "transparent"}}
                onMouseEnter={e => e.currentTarget.style.background = active ? "#1e1a10" : "#222018"}
                onMouseLeave={e => e.currentTarget.style.background = active ? "#1e1a10" : "transparent"}>
                {multi && <input type="checkbox" checked={active} onChange={() => toggle(ov)} style={{accentColor:"#e8a045"}} />}
                {ol}
              </label>
            );
          })}
          {multi && selected.length > 0 && <>
            <div style={{borderTop:"1px solid #2a2520", margin:"4px 0 0"}} />
            <button onClick={() => { onChange([]); setOpen(false); }}
              style={{width:"100%", padding:"5px 12px", background:"none", border:"none",
                color:"#8a8070", fontSize:10, fontFamily:"'IBM Plex Mono',monospace",
                cursor:"pointer", textAlign:"left"}}>Clear</button>
          </>}
        </div>
      )}
    </div>
  );
}

function fmt(n, dec=2) {
  if (n == null || isNaN(n)) return "–";
  return n.toFixed(dec);
}

// ─── CALCULATOR LOGIC ─────────────────────────────────────────────────────────
function calcHandheld(fl, crop, mp) {
  // max_time = 2√3 / (crop * fl * √mp)
  const maxTime = (2 * Math.sqrt(3)) / (crop * fl * Math.sqrt(mp));
  const shutter = 1 / maxTime;
  const diameter = fl; // relative, shown as ratio
  return { maxTime, shutter };
}

function calcRE(flC, apC, oisStops, flR, apR) {
  // RE = (flC/apC)² / (flR/apR)² × (flR/flC) = flC × (apR/apC)² / flR
  const re = (flC * Math.pow(apR / apC, 2)) / flR;
  const rePrime = re * Math.pow(2, oisStops);
  return { re, rePrime };
}

// ─── LENS EXPLORER ────────────────────────────────────────────────────────────
function LensExplorer() {
  const [search, setSearch] = useState("");
  const [typeF,   setTypeF]   = useState("all");
  const [oisF,    setOisF]    = useState("all");
  const [wrF,     setWrF]     = useState("all");
  const [formatF, setFormatF] = useState("all");
  const [sortBy,  setSortBy]  = useState("fl");
  const [brandF,  setBrandF]  = useState("all");
  const [afF,     setAfF]     = useState("all");

  const [sortDir, setSortDir] = useState(1);

  const brands = useMemo(() => {
    const s = new Set(LENSES.filter(l => formatF === "all" || l.format === formatF).map(l => l.brand));
    return ["all", ...Array.from(s).sort()];
  }, [formatF]);

  const filtered = useMemo(() => {
    let list = LENSES.filter(l => {
      if (typeF !== "all" && l.type !== typeF) return false;
      if (oisF !== "all" && String(l.ois) !== oisF) return false;
      if (wrF  !== "all" && String(l.wr)  !== wrF)  return false;
      if (formatF !== "all" && l.format !== formatF) return false;
      if (brandF !== "all" && l.brand !== brandF) return false;
      if (afF === "true"  && !l.af)  return false;
      if (afF === "false" &&  l.af)  return false;
      if (search) {
        const q = search.toLowerCase();
        if (!l.brand.toLowerCase().includes(q) && !l.model.toLowerCase().includes(q)) return false;
      }
      return true;
    });

    list.sort((a, b) => {
      let v = 0;
      if (sortBy === "fl")      v = a.flMin - b.flMin;
      else if (sortBy === "ap")     v = a.ap - b.ap;
      else if (sortBy === "weight") v = (a.kg||999) - (b.kg||999);
      else if (sortBy === "mtf")    v = (b.mtf||0) - (a.mtf||0);
      else if (sortBy === "price")  v = (a.price||99999) - (b.price||99999);
      else if (sortBy === "brand")  v = a.brand.localeCompare(b.brand);
      else if (sortBy === "model")  v = a.model.localeCompare(b.model);
      else if (sortBy === "type")   v = a.type.localeCompare(b.type);
      else if (sortBy === "thread") v = (a.thread||0) - (b.thread||0);
      else if (sortBy === "ois")    v = (a.ois ? 1 : 0) - (b.ois ? 1 : 0);
      else if (sortBy === "wr")     v = (a.wr  ? 1 : 0) - (b.wr  ? 1 : 0);
      else if (sortBy === "lm")     v = (a.lm  ? 1 : 0) - (b.lm  ? 1 : 0);
      return v * sortDir;
    });
    return list;
  }, [typeF, oisF, wrF, brandF, afF, formatF, search, sortBy, sortDir]);

  const Chip = ({ label, val, cur, set }) => (
    <button className={`chip${cur === val ? " on" : ""}`} onClick={() => set(val)}>{label}</button>
  );

  return (
    <div>
      <div className="filters">
        <div className="filter-group">
          <span className="filter-label">Mount</span>
          <Chip label="All"     val="all" cur={formatF} set={setFormatF} />
          <Chip label="X-Mount" val="X"   cur={formatF} set={setFormatF} />
          <Chip label="G-Mount" val="GFX" cur={formatF} set={setFormatF} />
        </div>
        <div className="filter-group">
          <span className="filter-label">Type</span>
          <Chip label="All" val="all" cur={typeF} set={setTypeF} />
          <Chip label="Prime" val="P" cur={typeF} set={setTypeF} />
          <Chip label="Zoom"  val="Z" cur={typeF} set={setTypeF} />
        </div>
        <div className="filter-group">
          <span className="filter-label">OIS</span>
          <Chip label="All"  val="all"   cur={oisF} set={setOisF} />
          <Chip label="Yes"  val="true"  cur={oisF} set={setOisF} />
          <Chip label="No"   val="false" cur={oisF} set={setOisF} />
        </div>
        <div className="filter-group">
          <span className="filter-label">WR</span>
          <Chip label="All"  val="all"   cur={wrF} set={setWrF} />
          <Chip label="Yes"  val="true"  cur={wrF} set={setWrF} />
          <Chip label="No"   val="false" cur={wrF} set={setWrF} />
        </div>
      </div>

      <div className="filters">
        <div className="filter-group">
          <span className="filter-label">AF</span>
          <Chip label="All" val="all"   cur={afF} set={setAfF} />
          <Chip label="AF"  val="true"  cur={afF} set={setAfF} />
          <Chip label="MF"  val="false" cur={afF} set={setAfF} />
        </div>
        <div className="filter-group">
          <span className="filter-label">Brand</span>
          <select className="sort-select" value={brandF} onChange={e => setBrandF(e.target.value)}>
            {brands.map(b => <option key={b} value={b}>{b === "all" ? "All" : b}</option>)}
          </select>
        </div>
      </div>

      <div className="filters">
        <input
          className="search-box"
          placeholder="search model..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <span className="count-badge">{filtered.length} / {LENSES.length} lenses</span>
      </div>

      <table>
        <thead>
          <tr>
            {[["brand","Brand"],["model","Model"],["type","Type"],["fl","FL (mm)"],["ap","f/"],["ois","OIS"],["wr","WR"],["lm","LM"],["mtf","MTF"],["weight","kg"],["thread","⌀mm"],["price","~€"]].map(([key, label]) => {
              const isNum = ["fl","ap","ois","wr","lm","mtf","weight","thread","price"].includes(key);
              return (
              <th key={key||"badge"} className={isNum ? "num" : ""} style={{cursor: key ? "pointer" : "default", userSelect:"none", whiteSpace:"nowrap"}}
                onClick={() => {
                  if (!key) return;
                  if (sortBy === key) setSortDir(d => d * -1);
                  else { setSortBy(key); setSortDir(1); }
                }}>
                {label}{sortBy === key ? (sortDir === 1 ? " ↑" : " ↓") : ""}
              </th>);
            })}
          </tr>
        </thead>
        <tbody>
          {filtered.map((l, i) => (
            <tr key={i} className="lens-row">
              <td className="brand">{l.brand}</td>
              <td className="model">{l.model}</td>
              <td><span className={`type-badge ${l.type}`}>{l.type}</span></td>
              <td className="num">
                {l.flMin === l.flMax ? l.flMin : `${l.flMin}–${l.flMax}`}
              </td>
              <td className="num">{l.ap}</td>
              <td><Dot yes={l.ois} /></td>
              <td><Dot yes={l.wr}  /></td>
              <td><Dot yes={l.lm}  /></td>
              <td className="num"><MtfPips val={l.mtf} /></td>
              <td className="num">{l.kg != null ? l.kg.toFixed(2) : "–"}</td>
              <td className="num">{l.thread || "–"}</td>
              <td className="num price">{l.price != null ? `~${l.price.toLocaleString()}` : "–"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {filtered.length === 0 && <div className="empty" style={{paddingTop:24}}>No lenses match the current filters.</div>}
      <div style={{marginTop:10, fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#4a4540"}}>
        ~ Prices are approximate and intended for budget planning only. See Trade Deals for current market rates.
      </div>
    </div>
  );
}

// ─── CAMERA DATA ──────────────────────────────────────────────────────────────
const CAMERAS = [
  // ── X-Pro ─────────────────────────────────────────────────────────────────
  { model:"X-Pro1",    mount:"X",   year:2012, mp:16,  sensor:"X-Trans I",         ibis:false, wr:false, video:"1080p", price:200,  est:true  },
  { model:"X-Pro2",    mount:"X",   year:2016, mp:24,  sensor:"X-Trans III",       ibis:false, wr:true,  video:"4K",    price:500,  est:true  },
  { model:"X-Pro3",    mount:"X",   year:2019, mp:26,  sensor:"X-Trans IV",        ibis:false, wr:true,  video:"4K",    price:1700, est:false },
  // ── X-T ───────────────────────────────────────────────────────────────────
  { model:"X-T1",      mount:"X",   year:2014, mp:16,  sensor:"X-Trans II",        ibis:false, wr:true,  video:"1080p", price:200,  est:true  },
  { model:"X-T2",      mount:"X",   year:2016, mp:24,  sensor:"X-Trans III",       ibis:false, wr:true,  video:"4K",    price:350,  est:true  },
  { model:"X-T3",      mount:"X",   year:2018, mp:26,  sensor:"X-Trans IV",        ibis:false, wr:true,  video:"4K",    price:600,  est:true  },
  { model:"X-T4",      mount:"X",   year:2020, mp:26,  sensor:"X-Trans IV",        ibis:true,  wr:true,  video:"4K",    price:800,  est:true  },
  { model:"X-T5",      mount:"X",   year:2022, mp:40,  sensor:"X-Trans V",         ibis:true,  wr:true,  video:"6.2K",  price:2000, est:false },
  { model:"X-T10",     mount:"X",   year:2015, mp:16,  sensor:"X-Trans II",        ibis:false, wr:false, video:"1080p", price:150,  est:true  },
  { model:"X-T20",     mount:"X",   year:2017, mp:24,  sensor:"X-Trans III",       ibis:false, wr:false, video:"4K",    price:250,  est:true  },
  { model:"X-T30",     mount:"X",   year:2019, mp:26,  sensor:"X-Trans IV",        ibis:false, wr:false, video:"4K",    price:400,  est:true  },
  { model:"X-T30 II",  mount:"X",   year:2021, mp:26,  sensor:"X-Trans IV",        ibis:false, wr:false, video:"4K",    price:550,  est:true  },
  { model:"X-T50",     mount:"X",   year:2024, mp:40,  sensor:"X-Trans V",         ibis:true,  wr:false, video:"6.2K",  price:1300, est:false },
  // ── X-H ───────────────────────────────────────────────────────────────────
  { model:"X-H1",      mount:"X",   year:2018, mp:24,  sensor:"X-Trans III",       ibis:true,  wr:true,  video:"4K",    price:500,  est:true  },
  { model:"X-H2",      mount:"X",   year:2022, mp:40,  sensor:"X-Trans V",         ibis:true,  wr:true,  video:"8K",    price:2500, est:false },
  { model:"X-H2S",     mount:"X",   year:2022, mp:26,  sensor:"X-Trans V Stacked", ibis:true,  wr:true,  video:"6.2K",  price:3000, est:false },
  // ── X-S ───────────────────────────────────────────────────────────────────
  { model:"X-S10",     mount:"X",   year:2020, mp:26,  sensor:"X-Trans IV",        ibis:true,  wr:false, video:"4K",    price:500,  est:true  },
  { model:"X-S20",     mount:"X",   year:2023, mp:26,  sensor:"X-Trans V",         ibis:true,  wr:false, video:"6.2K",  price:1300, est:false },
  // ── X-E ───────────────────────────────────────────────────────────────────
  { model:"X-E1",      mount:"X",   year:2012, mp:16,  sensor:"X-Trans I",         ibis:false, wr:false, video:"1080p", price:120,  est:true  },
  { model:"X-E2",      mount:"X",   year:2013, mp:16,  sensor:"X-Trans II",        ibis:false, wr:false, video:"1080p", price:150,  est:true  },
  { model:"X-E2S",     mount:"X",   year:2016, mp:16,  sensor:"X-Trans II",        ibis:false, wr:false, video:"1080p", price:200,  est:true  },
  { model:"X-E3",      mount:"X",   year:2017, mp:24,  sensor:"X-Trans III",       ibis:false, wr:false, video:"4K",    price:300,  est:true  },
  { model:"X-E4",      mount:"X",   year:2021, mp:26,  sensor:"X-Trans IV",        ibis:false, wr:false, video:"4K",    price:550,  est:true  },
  { model:"X-E5",      mount:"X",   year:2025, mp:40,  sensor:"X-Trans V",         ibis:false, wr:false, video:"4K",    price:900,  est:false },
  // ── X-M ───────────────────────────────────────────────────────────────────
  { model:"X-M1",      mount:"X",   year:2013, mp:16,  sensor:"Bayer",             ibis:false, wr:false, video:"1080p", price:120,  est:true  },
  { model:"X-M5",      mount:"X",   year:2024, mp:26,  sensor:"X-Trans V",         ibis:false, wr:false, video:"6.2K",  price:800,  est:false },
  // ── X-A ───────────────────────────────────────────────────────────────────
  { model:"X-A1",      mount:"X",   year:2013, mp:16,  sensor:"Bayer",             ibis:false, wr:false, video:"1080p", price:100,  est:true  },
  { model:"X-A2",      mount:"X",   year:2015, mp:16,  sensor:"Bayer",             ibis:false, wr:false, video:"1080p", price:100,  est:true  },
  { model:"X-A3",      mount:"X",   year:2016, mp:24,  sensor:"Bayer",             ibis:false, wr:false, video:"1080p", price:150,  est:true  },
  { model:"X-A5",      mount:"X",   year:2018, mp:24,  sensor:"Bayer",             ibis:false, wr:false, video:"4K",    price:200,  est:true  },
  { model:"X-A7",      mount:"X",   year:2019, mp:24,  sensor:"Bayer",             ibis:false, wr:false, video:"4K",    price:250,  est:true  },
  // ── GFX ───────────────────────────────────────────────────────────────────
  { model:"GFX 50S",   mount:"GFX", year:2017, mp:51,  sensor:"GFX CMOS",          ibis:false, wr:true,  video:"1080p", price:2000, est:true  },
  { model:"GFX 50R",   mount:"GFX", year:2018, mp:51,  sensor:"GFX CMOS",          ibis:false, wr:true,  video:"1080p", price:1500, est:true  },
  { model:"GFX 100",   mount:"GFX", year:2019, mp:102, sensor:"GFX CMOS II",       ibis:true,  wr:true,  video:"4K",    price:3500, est:true  },
  { model:"GFX 100S",  mount:"GFX", year:2021, mp:102, sensor:"GFX CMOS II",       ibis:true,  wr:true,  video:"4K",    price:3500, est:true  },
  { model:"GFX 50S II",mount:"GFX", year:2021, mp:51,  sensor:"GFX CMOS II",       ibis:true,  wr:true,  video:"4K",    price:3500, est:false },
  { model:"GFX 100 II",mount:"GFX", year:2023, mp:102, sensor:"GFX CMOS II HS",    ibis:true,  wr:true,  video:"8K",    price:7500, est:false },
  { model:"GFX 100S II",mount:"GFX",year:2024, mp:102, sensor:"GFX CMOS II HS",    ibis:true,  wr:true,  video:"8K",    price:5000, est:false },
  { model:"GFX 100RF", mount:"GFX", year:2025, mp:102, sensor:"GFX CMOS II HS",    ibis:false, wr:true,  video:"4K",    price:5000, est:false },
];

// ─── CAMERA EXPLORER ──────────────────────────────────────────────────────────
function CameraExplorer() {
  const [mountF, setMountF] = useState("all");
  const [ibisF,  setIbisF]  = useState("all");
  const [wrF,    setWrF]    = useState("all");
  const [sortBy, setSortBy] = useState("mount");
  const [sortDir, setSortDir] = useState(1);

  const filtered = useMemo(() => {
    let list = [...CAMERAS];
    if (mountF !== "all") list = list.filter(c => c.mount === mountF);
    if (ibisF  !== "all") list = list.filter(c => String(c.ibis) === ibisF);
    if (wrF    !== "all") list = list.filter(c => String(c.wr)   === wrF);
    list.sort((a, b) => {
      let v = 0;
      if      (sortBy === "mount")  v = a.mount.localeCompare(b.mount);
      else if (sortBy === "model")  v = a.model.localeCompare(b.model);
      else if (sortBy === "year")   v = a.year - b.year;
      else if (sortBy === "mp")     v = a.mp - b.mp;
      else if (sortBy === "sensor") v = a.sensor.localeCompare(b.sensor);
      else if (sortBy === "ibis")   v = (a.ibis ? 1 : 0) - (b.ibis ? 1 : 0);
      else if (sortBy === "wr")     v = (a.wr   ? 1 : 0) - (b.wr   ? 1 : 0);
      else if (sortBy === "video")  v = a.video.localeCompare(b.video);
      else if (sortBy === "price")  v = (a.price||99999) - (b.price||99999);
      return v * sortDir;
    });
    return list;
  }, [mountF, ibisF, wrF, sortBy, sortDir]);

  const Chip = ({ label, val, cur, set }) => (
    <button className={`chip${cur === val ? " on" : ""}`} onClick={() => set(val)}>{label}</button>
  );

  return (
    <div>
      <div className="filters">
        <div className="filter-group">
          <span className="filter-label">Mount</span>
          <Chip label="All"     val="all" cur={mountF} set={setMountF} />
          <Chip label="X-Mount" val="X"   cur={mountF} set={setMountF} />
          <Chip label="G-Mount" val="GFX" cur={mountF} set={setMountF} />
        </div>
        <div className="filter-group">
          <span className="filter-label">IBIS</span>
          <Chip label="All" val="all"   cur={ibisF} set={setIbisF} />
          <Chip label="Yes" val="true"  cur={ibisF} set={setIbisF} />
          <Chip label="No"  val="false" cur={ibisF} set={setIbisF} />
        </div>
        <div className="filter-group">
          <span className="filter-label">WR</span>
          <Chip label="All" val="all"   cur={wrF} set={setWrF} />
          <Chip label="Yes" val="true"  cur={wrF} set={setWrF} />
          <Chip label="No"  val="false" cur={wrF} set={setWrF} />
        </div>
      </div>

      <div style={{display:"flex", alignItems:"center", gap:8, marginBottom:10}}>
        <span className="count-badge">{filtered.length} cameras</span>
      </div>

      <table>
        <thead>
          <tr>
            {[["mount","Mount"],["model","Model"],["year","Year"],["mp","MP"],["sensor","Sensor"],["ibis","IBIS"],["wr","WR"],["video","Video"],["price","€"]].map(([key, label]) => (
              <th key={key}
                className={["year","mp","price"].includes(key) ? "num" : ""}
                style={{cursor:"pointer", userSelect:"none", whiteSpace:"nowrap"}}
                onClick={() => { if (sortBy === key) setSortDir(d => -d); else { setSortBy(key); setSortDir(1); } }}>
                {label}{sortBy === key ? (sortDir === 1 ? " ▲" : " ▼") : ""}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filtered.map((c, i) => (
            <tr key={i}>
              <td style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#8a8070"}}>{c.mount === "GFX" ? "G-Mount" : "X-Mount"}</td>
              <td className="model">{c.model}</td>
              <td className="num" style={{color:"#8a8070"}}>{c.year}</td>
              <td className="num">{c.mp}</td>
              <td style={{fontSize:11, color:"#b0a898"}}>{c.sensor}</td>
              <td style={{textAlign:"center"}}><Dot yes={c.ibis} /></td>
              <td style={{textAlign:"center"}}><Dot yes={c.wr} /></td>
              <td className="num" style={{color:"#8a8070"}}>{c.video}</td>
              <td className="num price">{c.price ? `~${c.price.toLocaleString()}` : "–"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {filtered.length === 0 && <div className="empty" style={{paddingTop:24}}>No cameras match.</div>}
    </div>
  );
}

function Calculator() {
  const [mp,    setMp]    = useState(26);
  const [crop,  setCrop]  = useState(1.5);
  const [refFl, setRefFl] = useState(35);
  const [refAp, setRefAp] = useState(1.4);
  const [refIso,setRefIso]= useState(1600);
  const [cmpFl, setCmpFl] = useState(16);
  const [cmpAp, setCmpAp] = useState(1.4);
  const [ois,   setOis]   = useState(0);

  const { maxTime: refTime, shutter: refShutter } = calcHandheld(refFl, crop, mp);
  const { maxTime: cmpTime, shutter: cmpShutter } = calcHandheld(cmpFl, crop, mp);
  const refDiam = refFl / refAp;
  const cmpDiam = cmpFl / cmpAp;
  const { re, rePrime } = calcRE(cmpFl, cmpAp, ois, refFl, refAp);
  const isoNeeded = refIso / rePrime;
  const reBarPct = Math.min(re * 100, 100);

  const Row = ({ label, val, min, max, step, set, unit, display }) => (
    <div className="field">
      <label>{label}</label>
      <input type="range" min={min} max={max} step={step}
        value={val} onChange={e => set(parseFloat(e.target.value))} />
      <span className="val">{display ? display(val) : val}</span>
      <span className="unit">{unit}</span>
    </div>
  );

  const IsoRow = ({ label, val, set }) => (
    <div className="field">
      <label>{label}</label>
      <input type="range" min={0} max={ISO_STEPS.length - 1} step={1}
        value={ISO_STEPS.indexOf(val) === -1 ? 4 : ISO_STEPS.indexOf(val)}
        onChange={e => set(ISO_STEPS[parseInt(e.target.value)])} />
      <span className="val">{val}</span>
      <span className="unit"></span>
    </div>
  );

  return (
    <div>
      <div style={{background:"#0f0d0b", border:"1px solid #1e1b16", padding:"12px 16px", marginBottom:18}}>
        <div style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#e8a045", textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:8}}>What this does</div>
        <div style={{fontSize:12, color:"#b0a898", lineHeight:1.7}}>
          <b style={{color:"#e0d8cc"}}>Relative Exposure</b> answers the question: <i>"if I switch from lens A to lens B, how much do I need to raise ISO to get the same exposure?"</i>
          {" "}Set your reference lens (the one you know), then dial in the compare lens. The result shows whether the new lens collects more or less light — and the ISO equivalent gap between them.
        </div>
        <div style={{fontSize:12, color:"#b0a898", lineHeight:1.7, marginTop:6}}>
          <b style={{color:"#e0d8cc"}}>Handheld shutter</b> shows the minimum shutter speed to avoid camera shake for each lens, based on your sensor resolution and crop factor.
        </div>
      </div>
      <div className="calc-grid">
        <div className="calc-panel">
          <h3>Reference lens</h3>
          <Row label="Sensor MP"   val={mp}     min={8}   max={60}  step={1}   set={setMp}     unit="MP" />
          <Row label="Crop factor" val={crop}   min={1}   max={2}   step={0.1} set={setCrop}   unit="×"  />
          <Row label="Focal length" val={refFl} min={6}   max={400} step={1}   set={setRefFl}  unit="mm" />
          <Row label="f-number"    val={refAp}  min={0.95}max={5.6} step={0.1} set={setRefAp}  unit="f/" />
          <IsoRow label="ISO" val={refIso} set={setRefIso} />
          <div className="results-row" style={{marginTop:14}}>
            <div className="result-cell">
              <div className="r-label">Entrance ⌀</div>
              <div className="r-val">{fmt(refDiam, 1)}</div>
              <div className="r-unit">mm</div>
            </div>
            <div className="result-cell">
              <div className="r-label">Max time</div>
              <div className="r-val">{fmt(refTime * 1000, 0)}</div>
              <div className="r-unit">ms</div>
            </div>
            <div className="result-cell">
              <div className="r-label">Shutter</div>
              <div className="r-val">1/{fmt(refShutter, 0)}</div>
              <div className="r-unit">sec</div>
            </div>
            <div className="result-cell">
              <div className="r-label">ISO ref</div>
              <div className="r-val">{refIso}</div>
              <div className="r-unit">ISO</div>
            </div>
          </div>
        </div>

        <div className="calc-panel">
          <h3>Compare lens (handheld light gathering)</h3>
          <Row label="Focal length" val={cmpFl} min={6}    max={400} step={1}   set={setCmpFl} unit="mm" />
          <Row label="f-number"     val={cmpAp} min={0.95} max={5.6} step={0.1} set={setCmpAp} unit="f/" />
          <Row label="OIS stops"    val={ois}   min={0}    max={5}   step={0.5} set={setOis}   unit="EV" />
          <div className="results-row" style={{marginTop:14}}>
            <div className="result-cell">
              <div className="r-label">Entrance ⌀</div>
              <div className="r-val">{fmt(cmpDiam, 1)}</div>
              <div className="r-unit">mm</div>
            </div>
            <div className="result-cell">
              <div className="r-label">Max time</div>
              <div className="r-val">{fmt(cmpTime * 1000, 0)}</div>
              <div className="r-unit">ms</div>
            </div>
            <div className="result-cell">
              <div className="r-label">Shutter</div>
              <div className="r-val">1/{fmt(cmpShutter, 0)}</div>
              <div className="r-unit">sec</div>
            </div>
            <div className="result-cell">
              <div className="r-label">ISO needed</div>
              <div className="r-val" style={{color: isoNeeded > 6400 ? "#c04030" : "#e8a045"}}>
                {fmt(isoNeeded, 0)}
              </div>
              <div className="r-unit">ISO</div>
            </div>
          </div>
        </div>
      </div>

      <div className="re-bar-wrap">
        <div className="re-bar-label">
          <span>Relative exposure (handheld): RE = {fmt(re, 3)}{ois > 0 ? ` → RE' = ${fmt(rePrime,3)} (with ${ois} EV OIS)` : ""}</span>
          <span style={{color: re >= 1 ? "#5a9060" : "#c07040"}}>
            {re >= 1 ? `+${fmt((re-1)*100,0)}% more light` : `${fmt((1-re)*100,0)}% less light`}
          </span>
        </div>
        <div className="re-bar-track">
          <div className="re-bar-fill" style={{width:`${Math.min(rePrime*100,100)}%`}} />
          <div style={{
            position:"absolute", top:0, left:"100%",
            transform:"translateX(-1px)",
            width:1, height:"100%", background:"#554f44"
          }} />
        </div>
        <div style={{display:"flex",justifyContent:"space-between",marginTop:4}}>
          <span style={{fontSize:9,color:"#8a8070",fontFamily:"'IBM Plex Mono',monospace"}}>0</span>
          <span style={{fontSize:9,color:"#8a8070",fontFamily:"'IBM Plex Mono',monospace"}}>= Reference</span>
        </div>
        <div style={{
          marginTop:12, fontSize:11, color:"#b0a898",
          fontFamily:"'IBM Plex Mono',monospace", lineHeight:"1.7",
          borderTop:"1px solid #1e1b16", paddingTop:10
        }}>
          <span style={{color:"#a09888"}}>RE = FL_cmp × (f_ref / f_cmp)² / FL_ref</span>
          {"  ·  "}
          <span style={{color:"#a09888"}}>Shutter rule = 2√3 / (crop × FL × √MP)</span>
          {"  ·  "}
          <span style={{color:"#a09888"}}>ISO_req = ISO_ref / RE'</span>
        </div>
      </div>
    </div>
  );
}

// ─── TRADE ────────────────────────────────────────────────────────────────────
function Trade() {
  const [sortBy, setSortBy] = useState("ratio");

  const sorted = useMemo(() => {
    return [...TRADE].sort((a, b) => {
      if (sortBy === "ratio")   return b.ratio - a.ratio;
      if (sortBy === "savings") return b.savings - a.savings;
      if (sortBy === "used")    return a.usedPrice - b.usedPrice;
      return 0;
    });
  }, [sortBy]);

  const maxRatio = Math.max(...TRADE.map(t => t.ratio));

  return (
    <div>
      <div className="filters" style={{marginBottom:14}}>
        <span className="filter-label">Sort by</span>
        {[["ratio","Savings Ratio"],["savings","€ Saved"],["used","Used Price"]].map(([v,l]) => (
          <button key={v} className={`chip${sortBy===v?" on":""}`} onClick={()=>setSortBy(v)}>{l}</button>
        ))}
        <span style={{marginLeft:"auto",fontSize:10,color:"#8a8070",fontFamily:"'IBM Plex Mono',monospace"}}>
          forum.fujix-forum.de
        </span>
      </div>

      <table>
        <thead>
          <tr>
            <th>Lens</th>
            <th className="num">New €</th>
            <th className="num">Used €</th>
            <th className="num">Saved €</th>
            <th>Ratio</th>
            <th>Priority</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((t, i) => (
            <tr key={i} className={`trade-row${t.top ? " top-deal" : ""}`}>
              <td className="model" style={{color: t.top ? "#e8c070" : "#a09080"}}>
                {t.model}
                {t.top && <span className="top-badge">★</span>}
              </td>
              <td className="num" style={{color:"#8a8070"}}>{t.newPrice.toLocaleString()}</td>
              <td className="num price">{t.usedPrice.toLocaleString()}</td>
              <td className="num" style={{color: t.savings > 0 ? "#5a9060" : "#c04030"}}>
                {t.savings > 0 ? "+" : ""}{t.savings.toLocaleString()}
              </td>
              <td>
                <div className="ratio-bar-wrap">
                  <div className="ratio-bar"
                    style={{width: t.ratio <= 0 ? 0 : `${Math.min(t.ratio/maxRatio*100,100)}px`}}
                  />
                  <span style={{
                    fontFamily:"'IBM Plex Mono',monospace",
                    fontSize:11,
                    color: t.ratio >= 1 ? "#e8a045" : t.ratio < 0 ? "#c04030" : "#a09888"
                  }}>
                    {t.ratio >= 0 ? "×" : ""}{t.ratio.toFixed(2)}
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{
        marginTop:16, fontSize:11, color:"#8a8070",
        fontFamily:"'IBM Plex Mono',monospace", lineHeight:1.8
      }}>
        ratio = (new − used) / used {"·"} ★ = marked as good deal
      </div>
    </div>
  );
}

// ─── GENRES ───────────────────────────────────────────────────────────────────
function Genres() {
  const [genre, setGenre] = useState("Landscape");

  const list = useMemo(() => GENRES.filter(g => g.genre === genre), [genre]);

  return (
    <div>
      <div className="genre-tabs">
        {GENRE_LIST.map(g => (
          <button
            key={g}
            className={`genre-btn${genre === g ? " active" : ""}`}
            onClick={() => setGenre(g)}
          >
            {g}
          </button>
        ))}
      </div>

      <table>
        <thead>
          <tr>
            <th>Brand</th>
            <th>Model</th>
            <th className="num">FL (mm)</th>
            <th className="num">f/</th>
            <th>OIS</th>
            <th>WR</th>
            <th className="num">MTF</th>
            <th className="num">kg</th>
            <th className="num">€</th>
            <th>Rec</th>
          </tr>
        </thead>
        <tbody>
          {list.map((g, i) => {
            const l = LENSES.find(x =>
              x.brand === g.brand && x.model === g.model
            );
            return (
              <tr key={i} style={g.top ? {background:"#0f0e0b"} : {}}>
                <td className="brand">{g.brand}</td>
                <td className="model">
                  {g.model}
                  {g.top && <span className="top-badge">TOP</span>}
                </td>
                <td className="num">{g.fl}</td>
                <td className="num">{l ? l.ap : "–"}</td>
                <td>{l ? <Dot yes={l.ois} /> : "–"}</td>
                <td>{l ? <Dot yes={l.wr}  /> : "–"}</td>
                <td className="num">{l ? <MtfPips val={l.mtf} /> : "–"}</td>
                <td className="num">{l ? l.kg : "–"}</td>
                <td className="num price">{l?.price != null ? `~${l.price.toLocaleString()}` : "–"}</td>
                <td>{g.top ? <span style={{color:"#e8a045",fontSize:12}}>★</span> : ""}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ─── MARK DOTS ────────────────────────────────────────────────────────────────
function MarkDots({ mark }) {
  if (mark == null) return <span style={{color:"#8a8070"}}>–</span>;
  const palette = ["","#2a2520","#4a4540","#7a7060","#c08830","#e8a045"];
  const dots    = "●".repeat(mark);
  return (
    <span style={{
      fontFamily:"'IBM Plex Mono',monospace",
      fontSize:10,
      color: palette[mark] || "#8a8070",
      letterSpacing:"0.1em"
    }}>
      {dots || "–"}
    </span>
  );
}

// ─── EV GUIDE ─────────────────────────────────────────────────────────────────
function EVGuide() {
  const [genre, setGenre]   = useState("Street");
  const [ev,    setEv]      = useState(2);
  const [sceneDesc, setSceneDesc] = useState("Lit street at night");
  const [iso,   setIso]     = useState(6400);
  const [nd,    setNd]      = useState([]);   // selected ND factors (stacked = product)
  const [showOis,setShowOis]= useState(false);
  const [sortBy,setSortBy]  = useState("top");
  const [sortDir,setSortDir]= useState(1); // 1=asc, -1=desc
  const [showAll,setShowAll]= useState(false);
  const [crop,   setCrop]   = useState(1.5);
  const [mp,     setMp]     = useState(26);  // sensor resolution for handheld formula
  const [aoV,    setAoV]    = useState(24);
  const [wildlifeSubject, setWildlifeSubject] = useState({size:1.5});
  const [tc, setTc] = useState(1.0); // tele converter multiplier
  const [lsWr,   setLsWr]   = useState(false);
  const [lsOis,  setLsOis]  = useState(false);
  const [lsTs,   setLsTs]   = useState(false);
  const [lsMode, setLsMode] = useState([]);
  const [lsPrice,setLsPrice]= useState(Infinity);
  const [lsMarks,setLsMarks]= useState([]);
  const [lsWeight,setLsWeight]= useState(Infinity);

  const [astroPrice,setAstroPrice]= useState(Infinity);
  const [astroMarks,setAstroMarks]= useState([]);
  const [brandFilter,setBrandFilter]= useState([]);
  const [mtfFilter,  setMtfFilter]  = useState([]);
  const [isMobile, setIsMobile] = useState(() => typeof window !== "undefined" && window.innerWidth < 640);
  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth < 640);
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);

  const GENRE_SCENE_FILTER = {
    Astronomy: s => s.ev <= 1,
    Landscape:    s => s.ev >= 7 && s.ev <= 16,
    Architecture: s => s.ev >= 3 && s.ev <= 12,
    Street:       s => s.ev >= -1 && s.ev <= 8,
    Travel:       s => s.ev >= 5 && s.ev <= 14,
    Portrait:     s => s.ev >= 5 && s.ev <= 14,
    Sport:        s => s.ev >= 6 && s.ev <= 16,
    Wildlife:     s => s.ev >= 5 && s.ev <= 14,
  };

  const visibleScenes = GENRE_SCENE_FILTER[genre]
    ? EV_SCENES.filter(GENRE_SCENE_FILTER[genre])
    : EV_SCENES;

  const sceneListRef = useRef(null);

  const scrollToEv = useCallback(() => {
    const container = sceneListRef.current;
    if (!container) return;
    const el = container.querySelector(`[data-ev="${ev}"]`);
    if (!el) return;
    const containerRect = container.getBoundingClientRect();
    const elRect = el.getBoundingClientRect();
    const offset = elRect.top - containerRect.top + container.scrollTop - containerRect.height / 2 + elRect.height / 2;
    container.scrollTop = Math.max(0, offset);
  }, [ev]);

  useEffect(() => { scrollToEv(); }, [ev, genre, scrollToEv]);
  useEffect(() => {
    const t1 = setTimeout(scrollToEv, 50);
    const t2 = setTimeout(scrollToEv, 300);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, []);

  const APERTURES = [1, 1.4, 2, 2.8, 4, 5.6, 8, 11, 16, 22];
  const params = GENRE_PARAMS[genre];

  // Auto-set sensible default scene when genre changes
  function handleGenre(g) {
    setGenre(g);
    setBrandFilter([]);
    setMtfFilter([]);
    setNd([]);
    setLsMarks([]); setLsPrice(Infinity); setLsMode([]); setLsOis(false); setLsWr(false); setLsTs(false); setLsWeight(Infinity);
    if      (g === "Astronomy")              { setEv(-7); setSceneDesc("Milky Way");         setIso(1600); setSortBy("fl"); setAoV(12); }
    else if (g === "Landscape")              { setEv(9);  setSceneDesc("10 min after sunset"); setIso(100);  setAoV(24); }
    else if (g === "Architecture")           { setEv(7);  setSceneDesc("Indoor daylight");     setIso(200);  setAoV(12); }
    else if (g === "Street")                 { setEv(2);  setSceneDesc("Lit street at night"); setIso(6400); setAoV(24); }
    else if (g === "Travel")                 { setEv(11); setSceneDesc("Golden hour");         setIso(400);  setAoV(24); }
    else if (g === "Portrait")               { setEv(10); setSceneDesc("Window light"); setIso(200); setAoV(57); }
    else if (g === "Sport")                  { setEv(13); setSceneDesc("Overcast outdoor");  setIso(800);  setAoV(135); }
    else if (g === "Wildlife")               { setEv(9);  setSceneDesc("Blue hour");          setIso(3200); setAoV(300); }
  }

  // Rule of 500: max exposure before star trails = 500 / (crop × FL)
  const rule500 = params.rule500 ? Math.round(500 / (1.5 * params.fl)) : null;

  function calcT(N) { return (N * N * 100) / (iso * Math.pow(2, ev)); }

  function fmtShutter(t) {
    if (t >= 120) return ">2m";
    if (t >= 30)  return `${Math.round(t)}"`;
    if (t >= 1)   return `${parseFloat(t.toFixed(1))}"`;
    const inv = 1 / t;
    if (inv >= 3000) return `1/${Math.round(inv/1000)*1000}`;
    if (inv >= 500)  return `1/${Math.round(inv/100)*100}`;
    if (inv >= 100)  return `1/${Math.round(inv/10)*10}`;
    return `1/${Math.round(inv)}`;
  }

  function cellColor(t) {
    if (rule500 != null) {
      // Astronomy: want t ≤ rule500 (no trails), as long as possible
      if (t <= rule500 && t >= rule500 / 2) return "#6aaa70";  // ideal range
      if (t < rule500 / 2 && t >= 2)        return "#b09040";  // too short, underexposing
      if (t < 2)                             return "#5a4838";  // useless for astro
      return "#905030";                                          // over limit — star trails
    }
    if (!params.minShutter) return "#8a8070";
    if (t >= params.minShutter * 4) return "#6aaa70";
    if (t >= params.minShutter)     return "#b09040";
    if (t >= params.minShutter / 4) return "#905030";
    return "#5a4838";
  }

  const isAstro     = genre === "Astronomy";
  const isLandscape    = genre === "Landscape" || genre === "Architecture";
  const isArchitecture = genre === "Architecture";
  const isStreet       = genre === "Street";
  const isTravel       = genre === "Travel";
  const isPortrait     = genre === "Portrait";
  const isSport        = genre === "Sport";
  const isWildlife     = genre === "Wildlife";
  const sweetSpot      = crop === 0.79 ? 11 : 8;
  const ndFactor       = nd.length === 0 ? 1 : nd.reduce((a, b) => a * b, 1);
  const hasMark    = isLandscape || !!(EV_LENSES[genre]?.[0]?.mark != null);
  const hasMarkOis = !isLandscape && !!(EV_LENSES[genre]?.[0]?.markOis != null);

  // Astro: ideal ISO so that exposure fits within rule-of-500 window
  // idealIso = f² × 100 / (maxT × 2^EV)
  function astroSuitability(l) {
    const ld = LENSES.find(x => x.brand === l.brand && x.model === l.model);
    if (!ld) return null;
    const fl       = ld.flMin;
    const ap       = ld.ap;
    const maxT     = 500 / (crop * fl);
    const idealIso = Math.round((ap * ap * 100) / (maxT * Math.pow(2, ev)));
    const actT     = (ap * ap * 100) / (iso * Math.pow(2, ev));
    const ratio    = actT / maxT;
    return { fl, ap, maxT, actT, idealIso, ratio, ois: ld.ois, wr: ld.wr };
  }

  // Handheld: max exposure time = 1 / (√(MP/12) × crop × FL)
  // idealIso    = ISO needed to handhold at lens's widest aperture (for other genre columns)
  // idealIsoRef = ISO needed at fRef = f/8 APS-C equiv (for landscape filtering — aperture-normalized)
  function handheldSuitability(l) {
    const ld = LENSES.find(x => x.brand === l.brand && x.model === l.model);
    if (!ld) return null;
    const fl         = ld.flMin;
    const ap         = ld.ap;
    const fRef       = 8 * crop / 1.5;
    const minShutter = isPortrait
      ? 1 / (2 * crop * fl)
      : (isSport || isWildlife)
      ? 1 / (4 * crop * fl)
      : 1 / (Math.sqrt(mp / 12) * crop * fl);
    const idealIso    = Math.round((ap   * ap   * 100) / (minShutter * Math.pow(2, ev)));
    const idealIsoRef = Math.round((fRef * fRef * 100) / (minShutter * Math.pow(2, ev)));
    return { fl, ap, minShutter, idealIso, idealIsoRef, ois: ld.ois, wr: ld.wr };
  }

  const TOLERANCE = 2.0;
  const sensorFormat = crop === 0.79 ? "GFX" : "X";

  const [lenses, filteredCount] = useMemo(() => {
    const fmt = crop === 0.79 ? "GFX" : "X"; // compute inline to avoid stale closure
    const isLS = genre === "Landscape" || genre === "Architecture";

    // Landscape uses full LENSES database; all other genres use curated EV_LENSES lists
    const source = isLS
      ? LENSES
          .filter(l => l.format === fmt)
          .filter(l => {
            // Show lenses that cover the selected FL:
            // zooms: selected aoV falls within the zoom's FF equiv range
            // primes: within 1 stop (×/÷ √2) of selected aoV
            const ffMin = l.flMin * crop;
            const ffMax = l.flMax * crop;
            if (l.flMin !== l.flMax) return ffMin <= aoV * 1.15 && ffMax >= aoV * 0.85;
            return ffMin >= aoV / Math.SQRT2 && ffMin <= aoV * Math.SQRT2;
          })
          .filter(l => {
            if (lsWr  && !l.wr)  return false;
            if (lsOis && !l.ois) return false;
            if (lsTs  && !(l.model.includes("T/S") || l.model.toLowerCase().includes("tilt") || l.model.toLowerCase().includes("shift"))) return false;
            if (l.price != null && l.price > lsPrice) return false;
            if (brandFilter.length > 0 && !brandFilter.includes(l.brand)) return false;
            if (mtfFilter.length > 0 && !mtfFilter.includes(l.mtf)) return false;
            if (lsWeight !== Infinity && l.kg != null && l.kg > lsWeight) return false;
            return true;
          })
          .map(l => {
            const mark = Math.max(1, l.mtf - 5);
            return { brand:l.brand, model:l.model, mtf:l.mtf, kg:l.kg, price:l.price, est:l.est, ois:l.ois, wr:l.wr, mark, markOis:null, top:false };
          })
          .filter(l => lsMarks.length === 0 || lsMarks.includes(l.mark))
      : (EV_LENSES[genre] || [])
          .filter(l => {
            const ld = LENSES.find(x => x.brand === l.brand && x.model === l.model);
            return !ld || ld.format === fmt;
          });

    let raw = source.map(l => ({
        ...l,
        _astro: isAstro ? astroSuitability(l) : null,
        _hh:   !isAstro ? handheldSuitability(l) : null,
      }));

    if (isAstro) {
      const ASTRO_FL_RANGE = { 12:[0,24], 24:[24,35], 50:[35,70], 135:[70,200], 300:[200,999] };
      const [flLo, flHi] = ASTRO_FL_RANGE[aoV] || [0,999];
      const passing  = raw.filter(l => {
        if (l._astro && l._astro.idealIso > iso * TOLERANCE) return false;
        if (l._astro) { const ff = l._astro.fl * crop; if (ff < flLo || ff > flHi) return false; }
        if (l.price != null && l.price > astroPrice) return false;
        if (brandFilter.length > 0 && !brandFilter.includes(l.brand)) return false;
        if (mtfFilter.length > 0 && !mtfFilter.includes(l.mtf)) return false;
        return true;
      });
      const excluded = raw.filter(l =>  l._astro && l._astro.idealIso >  iso * TOLERANCE)
                          .map(l => ({...l, _filtered: true}));
      const removed  = excluded.length;
      let list = showAll ? [...passing, ...excluded] : passing;
      list.sort((a, b) => {
        let v = 0;
        if (sortBy === "fl")     v = (a._astro?.fl ?? 99999) - (b._astro?.fl ?? 99999);
        else if (sortBy === "iso")    v = (a._astro?.idealIso ?? 99999) - (b._astro?.idealIso ?? 99999);
        else if (sortBy === "mark") {
          const am = a.mark ?? 0, bm = b.mark ?? 0;
          v = am !== bm ? bm - am : (b.top ? 1 : 0) - (a.top ? 1 : 0);
        }
        else if (sortBy === "price")  v = (a.price  || 99999) - (b.price  || 99999);
        else if (sortBy === "weight") v = (a.kg     || 99)    - (b.kg     || 99);
        else if (sortBy === "mtf")    v = (b.mtf    || 0)     - (a.mtf    || 0);
        else if (sortBy === "brand")  v = a.brand.localeCompare(b.brand);
        else v = (a._astro?.fl ?? 99999) - (b._astro?.fl ?? 99999);
        return v * sortDir;
      });
      if (astroMarks.length > 0) list = list.filter(l => astroMarks.includes(l.mark ?? null));
      return [list, removed];
    }

    // Architecture: filter lenses where exposure at sweet spot aperture > 30s at current ISO
    if (isArchitecture) {
      const ARCH_MAX_T = ndFactor > 1 ? Infinity : 30;
      const archT = l => (sweetSpot * sweetSpot * 100) / (iso * Math.pow(2, ev)) * ndFactor;
      const passing  = raw.filter(l => {
        if (l._hh && archT(l) > ARCH_MAX_T) return false;
        if (l.price != null && l.price > lsPrice) return false;
        if (lsMarks.length > 0 && !lsMarks.includes(l.mark)) return false;
        if (brandFilter.length > 0 && !brandFilter.includes(l.brand)) return false;
        if (lsTs && !(l.model.includes("T/S") || l.model.toLowerCase().includes("tilt") || l.model.toLowerCase().includes("shift"))) return false;
        if (lsWeight !== Infinity && l.kg != null && l.kg > lsWeight) return false;
        return true;
      });
      const excluded = raw.filter(l => l._hh && archT(l) > ARCH_MAX_T)
                          .map(l => ({...l, _filtered: true}));
      const removed  = excluded.length;
      let list = showAll ? [...passing, ...excluded] : passing;
      list.sort((a, b) => {
        let v = 0;
        if      (sortBy === "iso")    v = archT(a) - archT(b);
        else if (sortBy === "mark") { const am = a.mark ?? 0, bm = b.mark ?? 0; v = am !== bm ? bm - am : (b.top ? 1 : 0) - (a.top ? 1 : 0); }
        else if (sortBy === "price")  v = (a.price  || 99999) - (b.price  || 99999);
        else if (sortBy === "weight") v = (a.kg     || 99)    - (b.kg     || 99);
        else if (sortBy === "mtf")    v = (b.mtf    || 0)     - (a.mtf    || 0);
        else if (sortBy === "brand")  v = a.brand.localeCompare(b.brand);
        else v = (a._hh?.fl ?? 99999) - (b._hh?.fl ?? 99999);
        return v * sortDir;
      });
      return [list, removed];
    }

    // Landscape: show all lenses in FL range — Mode column informs, user decides
    // Other genres: filter lenses needing more than TOLERANCE× current ISO
    const passing  = isLS
      ? raw.filter(l => {
          if (lsMode.length === 0) return true;
          if (!l._hh) return false;
          const ref = l._hh.idealIsoRef;
          const cat = ref <= iso     ? "handheld"
                    : ref <= iso * 8 ? "OIS/IBIS"
                    :                  "tripod";
          return lsMode.includes(cat);
        })
      : raw.filter(l => {
          if (l._hh && l._hh.idealIso > iso * TOLERANCE) return false;
          if (isStreet || isTravel || isPortrait || isSport || isWildlife) {
            // FL range filter based on aoV selection
            const FL_RANGES = {12:[0,18], 24:[18,35], 50:[35,70], 135:[70,200], 300:[200,999], 15:[0,23], 33:[23,43], 57:[43,100]};
            const [flMin, flMax] = FL_RANGES[aoV] || [0, 999];
            if (l._hh && (l._hh.fl < flMin || l._hh.fl >= flMax)) return false;
            if (brandFilter.length > 0 && !brandFilter.includes(l.brand)) return false;
            if (mtfFilter.length > 0 && !mtfFilter.includes(l.mtf)) return false;
            if (lsMarks.length > 0 && !lsMarks.includes(l.mark)) return false;
            if (lsPrice !== Infinity && l.price != null && l.price > lsPrice) return false;
            if (lsWeight !== Infinity && l.kg != null && l.kg > lsWeight) return false;
            if (lsOis && !l.ois) return false;
            if (lsWr && !l.wr) return false;
            if (lsMode.length > 0) {
              if (!l._hh) return false;
              const cat = l._hh.idealIso <= iso ? "handheld" : l._hh.idealIso <= iso * 8 ? "OIS/IBIS" : "tripod";
              if (!lsMode.includes(cat)) return false;
            }
          }
          return true;
        });
    const excluded = isLS
      ? []
      : raw.filter(l =>  l._hh && l._hh.idealIso >  iso * TOLERANCE).map(l => ({...l, _filtered: true}));
    const removed  = excluded.length;
    let list = showAll ? [...passing, ...excluded] : passing;

    list.sort((a, b) => {
      let v = 0;
      const useOis = showOis && hasMarkOis;
      if (sortBy === "fl")    v = (a._hh?.fl ?? 99999) - (b._hh?.fl ?? 99999);
      else if (sortBy === "iso")   v = isArchitecture
        ? (() => { const at = (sweetSpot*sweetSpot*100)/(iso*Math.pow(2,ev)); return (Math.max(at, a._hh?.fl ? 1/(a._hh.fl*crop) : 0)) - (Math.max(at, b._hh?.fl ? 1/(b._hh.fl*crop) : 0)); })()
        : isLS
        ? (a._hh?.idealIsoRef ?? 99999) - (b._hh?.idealIsoRef ?? 99999)
        : (a._hh?.idealIso    ?? 99999) - (b._hh?.idealIso    ?? 99999);
      else if (sortBy === "top") {
        if (b.top !== a.top) return (b.top ? 1 : 0) - (a.top ? 1 : 0);
        const am = (useOis ? a.markOis : a.mark) ?? 0;
        const bm = (useOis ? b.markOis : b.mark) ?? 0;
        return bm - am;
      }
      else if (sortBy === "mark") {
        const am = (useOis ? a.markOis : a.mark) ?? 0;
        const bm = (useOis ? b.markOis : b.mark) ?? 0;
        if (am !== bm) return (bm - am);
        return (b.top ? 1 : 0) - (a.top ? 1 : 0);
      }
      else if (sortBy === "price")  v = (a.price  || 99999) - (b.price  || 99999);
      else if (sortBy === "weight") v = (a.kg     || 99)    - (b.kg     || 99);
      else if (sortBy === "mtf")    v = (b.mtf    || 0)     - (a.mtf    || 0);
      else if (sortBy === "brand")  v = a.brand.localeCompare(b.brand);
      return v * sortDir;
    });
    return [list, removed];
  }, [genre, sortBy, sortDir, showOis, ev, iso, showAll, crop, sensorFormat, aoV, mp, lsWr, lsOis, lsTs, lsMode, lsPrice, lsMarks, lsWeight, astroPrice, astroMarks, brandFilter, mtfFilter, ndFactor]);


  return (
    <div>
      {/* Genre selector */}
      <div className="genre-tabs">
        {GENRE_LIST.map(g => (
          <button key={g} className={`genre-btn${genre===g?" active":""}`} onClick={()=>handleGenre(g)}>{g}</button>
        ))}
      </div>

      <div style={{display:"grid", gridTemplateColumns:"220px 1fr", gap:14, marginBottom:18}}>

        {/* Left column */}
        <div style={{display:"flex", flexDirection:"column", gap:8}}>

        {/* Scene picker */}
        <div style={{background:"#0f0d0b", border:"1px solid #1e1b16"}}>
          <div style={{padding:"8px 12px 6px", fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#b0a898", textTransform:"uppercase", letterSpacing:"0.1em", borderBottom:"1px solid #1e1b16"}}>
            EV / Scene
          </div>
          <div ref={sceneListRef} style={{maxHeight:340, overflowY:"auto"}}>
            {visibleScenes.map((s, i) => (
              <div key={i}
                data-ev={s.ev}
                onClick={()=>{ setEv(s.ev); setSceneDesc(s.short); }}
                style={{
                  padding:"4px 10px", cursor:"pointer",
                  background: ev===s.ev ? "#1e1710" : "transparent",
                  borderLeft:`2px solid ${ev===s.ev ? "#e8a045" : "transparent"}`,
                  display:"flex", gap:10, alignItems:"center",
                }}>
                <span style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:11, color:"#e8a045", width:18, textAlign:"right", flexShrink:0}}>{s.ev}</span>
                <span style={{fontSize:11, color: ev===s.ev ? "#e0d8cc" : "#b0a898"}}>{GENRE_EV_LABELS[genre]?.[s.ev] ?? s.short}</span>
              </div>
            ))}
          </div>
        </div>

        {(() => {
          const GEAR = {
            Astronomy:    ["Star tracker","Sturdy tripod","Lens heater","Dew shield","Light pollution filter","External power bank","Remote intervalometer","Bahtinov mask","Spare batteries","Red light headlamp"],
            Landscape:    ["Sturdy tripod","Ball head","L-bracket","Remote shutter","Filter set (CPL & ND)","Graduated ND filter","Rain cover","Spare batteries","Fast memory cards","Outdoor camera backpack"],
            Architecture: ["Sturdy tripod","Geared tripod head","L-bracket","Remote shutter","Tethering cable","Field monitor","Filter set (CPL & Graduated ND)","Anti-reflective lens cover","Color checker","Power bank"],
            Street:       ["Thumb grip","Compact bag","Quick-adjust sling strap","Mini travel tripod","Flash (Compact)","Filter set (ND, CPL & Black Mist)","Fast memory cards","Spare batteries","Soft shutter release button","Rain cover"],
            Travel:       ["Travel tripod","Adjustable sling strap","Travel camera backpack","L-bracket","Filter set (ND & Polarizer)","Anti-reflection hood","Remote shutter","Fast memory cards","Spare batteries","Portable SSD"],
            Portrait:     ["Tripod","Speedlight","Flash trigger","Light stand","Constant light","Light modifiers","Reflector","Tethering cable","Color checker","Remote shutter"],
            Sport:        ["Monopod","Battery grip","Dual harness","Teleconverter","Remote trigger","Fast memory cards","Spare batteries","Rain cover","Power bank","Camera gear bag"],
            Wildlife:     ["Gimbal head","Tripod/Monopod","Teleconverter","Beanbag","Shoulder sling strap","Lens covers","Fast memory cards","Spare batteries","Power bank","Wildlife backpack"],
          };
          const items = GEAR[genre];
          if (!items) return null;
          return (
            <div style={{background:"#0f0d0b", border:"1px solid #1e1b16"}}>
            <div style={{padding:"8px 12px 6px", fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#b0a898", textTransform:"uppercase", letterSpacing:"0.1em", borderBottom:"1px solid #1e1b16"}}>Equipment</div>
              <div style={{padding:"8px 10px", fontFamily:"system-ui, sans-serif", fontSize:11, color:"#7a7268", lineHeight:1.6}}>
                {items.join(" · ")}
              </div>
            </div>
          );
        })()}

        </div>{/* end left column */}

        {/* Exposure results */}
        <div style={{background:"#0f0d0b", border:"1px solid #1e1b16", padding:"10px 14px"}}>
          <div style={{display:"flex", justifyContent:"space-between", alignItems:"baseline", marginBottom:12, paddingBottom:8, borderBottom:"1px solid #1e1b16"}}>
            <span style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:11, color:"#e0d8cc"}}>
              EV {ev} — {GENRE_EV_LABELS[genre]?.[ev] ?? EV_SCENES.find(s => s.ev === ev)?.short}
            </span>
            <span style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#8a8070"}}>
              {isArchitecture
                ? "Tripod · maximize depth of field · find the sweet spot"
                : params.label}
            </span>
          </div>

          {/* Mount */}
          <div className="field" style={{marginBottom:10}}>
            <label>Mount</label>
            <div style={{display:"flex", gap:4}}>
              {[["X-Mount",1.5],["G-Mount",0.79]].map(([label,c]) => (
                <button key={label} className={`chip${crop===c?" on":""}`}
                  onClick={()=>{ setCrop(c); setMp(c === 0.79 ? 102 : 26); if(isAstro) setIso(c === 0.79 ? 3200 : 1600); }}
                  style={{padding:"2px 8px"}}>
                  {label}{crop===c ? ` · ${c}×` : ""}
                </button>
              ))}
            </div>
            <span className="unit"></span>
          </div>

          {/* FL — Architecture only */}
          {isArchitecture && (
            <div className="field" style={{marginBottom:10}}>
              <label>FL</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
                {[
                  {label:"Ultra-wide", fl:12},
                  {label:"Wide",       fl:24},
                  {label:"Standard",   fl:50},
                  {label:"Tele",       fl:135},
                  {label:"Super-tele", fl:300},
                ].map(({label, fl}) => (
                  <button key={fl} className={`chip${aoV===fl?" on":""}`}
                    onClick={() => setAoV(fl)} style={{padding:"2px 8px"}}>{label}</button>
                ))}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {isAstro && (
            <div className="field" style={{marginBottom:10}}>
              <label>FL</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
                {[
                  {label:"Ultra-wide", fl:12},
                  {label:"Wide",       fl:24},
                  {label:"Standard",   fl:50},
                  {label:"Tele",       fl:135},
                  {label:"Super-tele", fl:300},
                ].map(({label, fl}) => (
                  <button key={fl} className={`chip${aoV===fl?" on":""}`}
                    onClick={() => setAoV(fl)} style={{padding:"2px 8px"}}>{label}</button>
                ))}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {(isStreet || isTravel) && (
            <div className="field" style={{marginBottom:10}}>
              <label>FL</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
                {[
                  {label:"Ultra-wide", fl:12},
                  {label:"Wide",       fl:24},
                  {label:"Standard",   fl:50},
                  {label:"Tele",       fl:135},
                  {label:"Super-tele", fl:300},
                ].map(({label, fl}) => (
                  <button key={fl} className={`chip${aoV===fl?" on":""}`}
                    onClick={() => setAoV(fl)} style={{padding:"2px 8px"}}>{label}</button>
                ))}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {isPortrait && (
            <div className="field" style={{marginBottom:10}}>
              <label>FL</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
                {[
                  {label:"Group",   fl:15},
                  {label:"Indoor",  fl:33},
                  {label:"Outdoor", fl:57},
                ].map(({label, fl}) => (
                  <button key={fl} className={`chip${aoV===fl?" on":""}`}
                    onClick={() => setAoV(fl)} style={{padding:"2px 8px"}}>{label}</button>
                ))}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {(isSport || isWildlife) && (
            <div className="field" style={{marginBottom:10}}>
              <label>FL</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
                {[
                  {label:"Standard",   fl:50},
                  {label:"Tele",       fl:135},
                  {label:"Super-tele", fl:300},
                ].map(({label, fl}) => (
                  <button key={fl} className={`chip${aoV===fl?" on":""}`}
                    onClick={() => setAoV(fl)} style={{padding:"2px 8px"}}>{label}</button>
                ))}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {isWildlife && (
            <div className="field" style={{marginBottom:10}}>
              <label>Subject</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
                {[
                  {label:"Large",  size:1.5},
                  {label:"Medium", size:0.5},
                  {label:"Small",  size:0.3},
                  {label:"Bird",   size:0.2},
                ].map(({label, size}) => (
                  <button key={size} className={`chip${wildlifeSubject.size===size?" on":""}`}
                    onClick={() => setWildlifeSubject({size})} style={{padding:"2px 8px"}}>{label}</button>
                ))}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {(isSport || isWildlife) && (
            <div className="field" style={{marginBottom:10}}>
              <label>TC</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
                {[
                  {label:"None", val:1.0},
                  {label:"1.4×", val:1.4},
                  {label:"2.0×", val:2.0},
                ].map(({label, val}) => (
                  <button key={val} className={`chip${tc===val?" on":""}`}
                    onClick={() => setTc(val)} style={{padding:"2px 8px"}}>{label}</button>
                ))}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {/* FL — Landscape only */}
          {genre === "Landscape" && (
            <div className="field" style={{marginBottom:10}}>
              <label>FL</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
                {[
                  {label:"Ultra-wide", fl:12},
                  {label:"Wide",       fl:24},
                  {label:"Standard",   fl:50},
                  {label:"Tele",       fl:135},
                  {label:"Super-tele", fl:300},
                ].map(({label, fl}) => (
                  <button key={fl} className={`chip${aoV===fl?" on":""}`}
                    onClick={() => setAoV(fl)} style={{padding:"2px 8px"}}>{label}</button>
                ))}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {/* ISO */}
          <div className="field" style={{marginBottom:10}}>
            <label>ISO</label>
            <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
              {(crop === 0.79
                ? [100, 200, 400, 800, 1600, 3200, 6400, 12800]
                : [100, 200, 400, 800, 1600, 3200, 6400]
              ).map(v => (
                <button key={v} className={`chip${iso===v?" on":""}`}
                  onClick={() => setIso(v)} style={{padding:"2px 8px"}}>
                  {v}
                </button>
              ))}
            </div>
            <span className="unit"></span>
          </div>

          {/* ND filter — Architecture and Landscape */}
          {(isArchitecture || genre === "Landscape") && (
            <div className="field" style={{marginBottom:4}}>
              <label>ND</label>
              <div style={{display:"flex", gap:3, flexWrap:"wrap", alignItems:"center"}}>
                {[2, 4, 8, 64, 1000].map(v => (
                  <button key={v} className={`chip${nd.includes(v)?" on":""}`}
                    onClick={() => setNd(s => s.includes(v) ? s.filter(x=>x!==v) : [...s,v])}
                    style={{padding:"2px 8px"}}>
                    ND{v.toLocaleString()}
                  </button>
                ))}
                {nd.length > 0 && (
                  <span style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#e8a045", marginLeft:4}}>
                    = ND{ndFactor.toLocaleString()}
                  </span>
                )}
                {nd.length > 0 && (
                  <button onClick={() => setNd([])}
                    style={{background:"none", border:"none", color:"#8a8070", fontSize:10,
                      fontFamily:"'IBM Plex Mono',monospace", cursor:"pointer", padding:"2px 6px"}}>
                    ✕
                  </button>
                )}
              </div>
              <span className="unit"></span>
            </div>
          )}

          {/* MP — not relevant for Astro or Architecture (tripod, no shake formula) */}
          {!isAstro && !isArchitecture && genre !== "Landscape" && !isSport && !isWildlife && <div className="field" style={{marginBottom:4}}>
            <label>MP</label>
            <div style={{display:"flex", gap:3, flexWrap:"wrap"}}>
              {(crop === 0.79 ? [51, 102] : [16, 24, 26, 40]).map(v => (
                <button key={v} className={`chip${mp===v?" on":""}`}
                  onClick={() => setMp(v)} style={{padding:"2px 8px"}}>
                  {v}
                </button>
              ))}
            </div>
            <span className="unit">MP</span>
          </div>}

          <div style={{borderTop:"1px solid #2e2a22", margin:"14px 0"}} />

          {isAstro ? (
            <div>
              <div style={{fontSize:10, color:"#8a8070", fontFamily:"'IBM Plex Mono',monospace", marginBottom:8, textTransform:"uppercase", letterSpacing:"0.06em"}}>
                Rule of 500 · untracked · ISO {iso}
              </div>
              <div style={{overflowX:"auto"}}>
                <table style={{borderCollapse:"collapse", fontSize:10, fontFamily:"'IBM Plex Mono',monospace"}}>
                  {(() => {
                    const FL_COLS = {
                      12:  [6, 8, 10, 12, 14, 16],
                      24:  [18, 21, 24, 28, 35],
                      50:  [35, 40, 50, 56],
                      135: [75, 85, 100, 135],
                      300: [200, 300, 400],
                    };
                    const cols = FL_COLS[aoV] || FL_COLS[12];
                    return (<>
                      <thead>
                        <tr>
                          <th style={{padding:"4px 8px", color:"#8a8070", textAlign:"left", borderBottom:"1px solid #2a2520"}}>f/</th>
                          {cols.map(fl => (
                            <th key={fl} style={{padding:"4px 8px", color:"#8a8070", textAlign:"center", borderBottom:"1px solid #2a2520"}}>{fl}mm</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {[1.0,1.2,1.4,1.8,2.0,2.8,4.0].map(ap => (
                          <tr key={ap}>
                            <td style={{padding:"4px 8px", color:"#e8a045", borderRight:"1px solid #2a2520"}}>{ap}</td>
                            {cols.map(fl => {
                              const maxT   = Math.round(500 / (crop * fl));
                              const needed = Math.round((ap * ap * 100) / (maxT * Math.pow(2, ev)));
                              const viable   = needed <= iso;
                              const marginal = !viable && needed <= iso * 1.5;
                              const color  = viable ? "#6aaa70" : marginal ? "#b09040" : "#905030";
                              const bg     = viable ? "#0e180e" : marginal ? "#181610" : "#180e0e";
                              const label  = maxT >= 60 ? `${Math.round(maxT/60)}m` : `${maxT}s`;
                              return (
                                <td key={fl} style={{padding:"4px 8px", textAlign:"center", background:bg, color, fontWeight: viable ? 600 : 400}}>
                                  {label}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </>);
                  })()}
                </table>
              </div>
              <div style={{marginTop:8, fontSize:10, fontFamily:"'IBM Plex Mono',monospace", color:"#8a8070"}}>
                <span style={{color:"#6aaa70"}}>●</span> within ISO {"  "}
                <span style={{color:"#b09040"}}>●</span> within 1 stop {"  "}
                <span style={{color:"#905030"}}>●</span> needs more ISO
              </div>
            </div>
          ) : isArchitecture ? (
            <div>
              <div style={{fontSize:10, color:"#8a8070", fontFamily:"'IBM Plex Mono',monospace", marginBottom:8, textTransform:"uppercase", letterSpacing:"0.06em"}}>
                Exposure matrix · ISO {iso}{ndFactor > 1 ? ` · ND${ndFactor.toLocaleString()}` : ""} · EV {ev} · sweet spot {crop !== 0.79 ? "f/8" : "f/11"}
              </div>
              <div style={{overflowX:"auto"}}>
                <table style={{borderCollapse:"collapse", fontSize:10, fontFamily:"'IBM Plex Mono',monospace"}}>
              {(() => {
                const FL_COLS = {
                  12:  [8, 10, 12, 14, 16],
                  24:  [18, 21, 24, 28, 35],
                  50:  [35, 40, 50, 56],
                  135: [75, 85, 100, 135],
                  300: [200, 300, 400],
                };
                const cols = FL_COLS[aoV] || [8,12,14,16,21,24,28,35];
                return (<>
                  <thead>
                    <tr>
                      <th style={{padding:"4px 8px", color:"#8a8070", textAlign:"left", borderBottom:"1px solid #2a2520"}}>f/</th>
                      {cols.map(fl => (
                        <th key={fl} style={{padding:"4px 8px", color:"#8a8070", textAlign:"center", borderBottom:"1px solid #2a2520"}}>{fl}mm</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {[2.8,4,5.6,8,11,16].map(ap => {
                      const isSweetSpot = ap === sweetSpot;
                      return (
                        <tr key={ap} style={{background: isSweetSpot ? "#141210" : "transparent"}}>
                          <td style={{padding:"4px 8px", color: isSweetSpot ? "#e8a045" : "#8a8070", borderRight:"1px solid #2a2520", fontWeight: isSweetSpot ? 600 : 400}}>{ap}{isSweetSpot ? " ★" : ""}</td>
                          {cols.map(fl => {
                            const t = (ap * ap * 100) / (iso * Math.pow(2, ev)) * ndFactor;
                            const color = t <= 1/60 ? "#4090d0" : t <= 30 ? "#d06040" : "#40d0b0";
                            const bg    = t <= 1/60 ? "#0e1820" : t <= 30 ? "#1a1008" : "#0e1e1c";
                            const label = t < 1 ? `1/${Math.round(1/t)}` : t < 60 ? `${Math.round(t)}s` : `${Math.round(t/60)}m`;
                            return (
                              <td key={fl} style={{padding:"4px 8px", textAlign:"center", background:bg, color, fontWeight: t > 30 ? 600 : 400}}>
                                {label}
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
                  </tbody>
                </>);
              })()}
                </table>
              </div>
              <div style={{marginTop:8, fontSize:10, fontFamily:"'IBM Plex Mono',monospace", color:"#8a8070"}}>
                <span style={{color:"#40d0b0"}}>●</span> people vanish {"  "}
                <span style={{color:"#d06040"}}>●</span> people blur {"  "}
                <span style={{color:"#4090d0"}}>●</span> people frozen
              </div>
            </div>
          ) : genre === "Landscape" ? (
            <div>
              <div style={{fontSize:10, color:"#8a8070", fontFamily:"'IBM Plex Mono',monospace", marginBottom:8, textTransform:"uppercase", letterSpacing:"0.06em"}}>
                Shutter speed matrix · ISO {iso}{ndFactor > 1 ? ` · ND${ndFactor.toLocaleString()}` : ""} · EV {ev} · tripod
              </div>
              <div style={{overflowX:"auto"}}>
                <table style={{borderCollapse:"collapse", fontSize:10, fontFamily:"'IBM Plex Mono',monospace"}}>
                  {(() => {
                    const FL_COLS = {
                      12:  [8, 10, 12, 14, 16],
                      24:  [18, 21, 24, 28, 35],
                      50:  [35, 40, 50, 56],
                      135: [75, 85, 100, 135],
                      300: [200, 300, 400],
                    };
                    const cols = FL_COLS[aoV] || FL_COLS[24];
                    const diffLimit = crop !== 0.79 ? 11 : 16;
                    const aps = [2.8, 4, 5.6, 8, 11, 16].filter(ap => ap <= diffLimit);
                    return (<>
                      <thead>
                        <tr>
                          <th style={{padding:"4px 8px", color:"#8a8070", textAlign:"left", borderBottom:"1px solid #2a2520"}}>f/</th>
                          {cols.map(fl => (
                            <th key={fl} style={{padding:"4px 8px", color:"#8a8070", textAlign:"center", borderBottom:"1px solid #2a2520"}}>{fl}mm</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {aps.map(ap => {
                          const diffWarn = (crop !== 0.79 && ap === 16) || (crop === 0.79 && ap === 22);
                          return (
                            <tr key={ap}>
                              <td style={{padding:"4px 8px", color: diffWarn ? "#b09040" : "#8a8070", borderRight:"1px solid #2a2520"}}>
                                {ap}{diffWarn ? " ⚠" : ""}
                              </td>
                              {cols.map(fl => {
                                const t = (ap * ap * 100) / (iso * Math.pow(2, ev)) * ndFactor;
                                const cat = t < 1 ? "static" : t <= 30 ? "silk" : "dramatic";
                                const color = cat === "static" ? "#4090d0" : cat === "silk" ? "#6aaa70" : "#40d0b0";
                                const bg    = cat === "static" ? "#0e1820" : cat === "silk" ? "#141e14" : "#0e1818";
                                const label = t < 1 ? `1/${Math.round(1/t)}` : t < 60 ? `${Math.round(t)}s` : `${Math.round(t/60)}m`;
                                return (
                                  <td key={fl} style={{padding:"4px 8px", textAlign:"center", background:bg, color, fontWeight: cat === "dramatic" ? 600 : 400}}>
                                    {label}
                                  </td>
                                );
                              })}
                            </tr>
                          );
                        })}
                      </tbody>
                    </>);
                  })()}
                </table>
              </div>
              <div style={{marginTop:8, fontSize:10, fontFamily:"'IBM Plex Mono',monospace", color:"#8a8070"}}>
                <span style={{color:"#4090d0"}}>●</span> static {"  "}
                <span style={{color:"#6aaa70"}}>●</span> silk (1–30s) {"  "}
                <span style={{color:"#40d0b0"}}>●</span> dramatic (&gt;30s) {"  "}
                <span style={{color:"#b09040"}}>⚠</span> {crop !== 0.79 ? "diffraction f/11+ (APS-C)" : "diffraction f/16+ (GFX)"}
              </div>
            </div>
          ) : (isStreet || isTravel || isPortrait) ? (
            <div>
              <div style={{fontSize:10, color:"#8a8070", fontFamily:"'IBM Plex Mono',monospace", marginBottom:8, textTransform:"uppercase", letterSpacing:"0.06em"}}>
                Reciprocal rule · min shutter by FL · ISO {iso} · EV {ev}
              </div>
              <div style={{overflowX:"auto"}}>
                <table style={{borderCollapse:"collapse", fontSize:10, fontFamily:"'IBM Plex Mono',monospace"}}>
                  {(() => {
                    const FL_COLS = {
                      12:  [8, 10, 12, 14, 16],
                      24:  [18, 21, 24, 28, 35],
                      50:  [35, 40, 50, 56],
                      135: [75, 85, 100, 135],
                      15:  [12, 15, 18, 23],
                      33:  [23, 28, 33, 40],
                      57:  [50, 57, 75, 85],
                      300: [200, 300, 400],
                    };
                    const cols = FL_COLS[aoV] || FL_COLS[24];
                    return (<>
                      <thead>
                        <tr>
                          <th style={{padding:"4px 8px", color:"#8a8070", textAlign:"left", borderBottom:"1px solid #2a2520"}}>f/</th>
                          {cols.map(fl => (
                            <th key={fl} style={{padding:"4px 8px", color:"#8a8070", textAlign:"center", borderBottom:"1px solid #2a2520"}}>{fl}mm</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {[1.0,1.2,1.4,1.8,2.0,2.8,4.0].map(ap => (
                          <tr key={ap}>
                            <td style={{padding:"4px 8px", color:"#e8a045", borderRight:"1px solid #2a2520"}}>{ap}</td>
                            {cols.map(fl => {
                              const minS   = isPortrait
                                ? 1 / (2 * crop * fl)
                                : (isSport || isWildlife)
                                ? 1 / (4 * crop * fl)
                                : 1 / (Math.sqrt(mp/12) * crop * fl);
                              const needed = Math.round((ap * ap * 100) / (minS * Math.pow(2, ev)));
                              const viable   = needed <= iso;
                              const marginal = !viable && needed <= iso * 1.5;
                              const color  = viable ? "#6aaa70" : marginal ? "#b09040" : "#905030";
                              const bg     = viable ? "#0e180e" : marginal ? "#181610" : "#180e0e";
                              const label  = minS >= 1 ? `${Math.round(minS)}s` : `1/${Math.round(1/minS)}`;
                              return (
                                <td key={fl} style={{padding:"4px 8px", textAlign:"center", background:bg, color, fontWeight: viable ? 600 : 400}}>
                                  {label}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </>);
                  })()}
                </table>
              </div>
              <div style={{marginTop:8, fontSize:10, fontFamily:"'IBM Plex Mono',monospace", color:"#8a8070"}}>
                <span style={{color:"#6aaa70"}}>●</span> within ISO {"  "}
                <span style={{color:"#b09040"}}>●</span> within 1 stop {"  "}
                <span style={{color:"#905030"}}>●</span> needs more ISO
              </div>
            </div>
          ) : (isSport || isWildlife) ? (
            <div>
              <div style={{fontSize:10, color:"#8a8070", fontFamily:"'IBM Plex Mono',monospace", marginBottom:8, textTransform:"uppercase", letterSpacing:"0.06em"}}>
                Shutter speed · 4× FL rule · ISO {iso} · EV {ev}
              </div>
              <div style={{overflowX:"auto"}}>
                <table style={{borderCollapse:"collapse", fontSize:10, fontFamily:"'IBM Plex Mono',monospace"}}>
                  {(() => {
                    const FL_COLS = {
                      50:  [50, 57, 75, 85],
                      135: [85, 100, 135, 200],
                      300: [200, 300, 400, 600],
                    };
                    const baseCols = FL_COLS[aoV] || FL_COLS[135];
                    const cols = baseCols.map(fl => Math.round(fl * tc));
                    const apShift = tc === 2.0 ? 2 : tc === 1.4 ? 1 : 0;
                    return (<>
                      <thead>
                        <tr>
                          <th style={{padding:"4px 8px", color:"#8a8070", textAlign:"left", borderBottom:"1px solid #2a2520"}}>f/</th>
                          {cols.map(fl => (
                            <th key={fl} style={{padding:"4px 8px", color:"#8a8070", textAlign:"center", borderBottom:"1px solid #2a2520"}}>{fl}mm</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {[2.0, 2.8, 4.0, 5.6].map(ap => {
                          const effAp = ap * Math.pow(Math.sqrt(2), apShift);
                          return (
                          <tr key={ap}>
                            <td style={{padding:"4px 8px", color:"#e8a045", borderRight:"1px solid #2a2520"}}>
                              {ap}
                            </td>
                            {cols.map(fl => {
                              const minS = 1 / (4 * crop * fl);
                              const t    = (effAp * effAp * 100) / (iso * Math.pow(2, ev));
                              const viable   = t <= minS;
                              const marginal = !viable && t <= minS * 2;
                              const color = viable ? "#6aaa70" : marginal ? "#b09040" : "#905030";
                              const bg    = viable ? "#0e180e" : marginal ? "#181610" : "#180e0e";
                              const tCapped = Math.max(t, 1/32000);
                              const label = tCapped < 1 ? `1/${Math.round(1/tCapped)}` : `${Math.round(tCapped)}s`;
                              return (
                                <td key={fl} style={{padding:"4px 8px", textAlign:"center", background:bg, color, fontWeight: viable ? 600 : 400}}>
                                  {label}
                                </td>
                              );
                            })}
                          </tr>
                          );
                        })}
                      </tbody>
                    </>);
                  })()}
                </table>
              </div>
              <div style={{marginTop:8, fontSize:10, fontFamily:"'IBM Plex Mono',monospace", color:"#8a8070"}}>
                <span style={{color:"#6aaa70"}}>●</span> fast enough {"  "}
                <span style={{color:"#b09040"}}>●</span> 1 stop slow {"  "}
                <span style={{color:"#905030"}}>●</span> too slow
              </div>
            </div>
          ) : (
            <div>
              <div style={{fontSize:10, color:"#8a8070", fontFamily:"'IBM Plex Mono',monospace", marginBottom:8, textTransform:"uppercase", letterSpacing:"0.06em"}}>
                Handheld at f/2 — min ISO by focal length at EV {ev}
              </div>
              <div style={{display:"flex", gap:1, flexWrap:"wrap"}}>
                {[8, 12, 16, 18, 23, 27, 35, 50, 85, 135, 200, 300, 400].map(fl => {
                  const idealIso = Math.round(400 * crop * fl / Math.pow(2, ev));
                  const viable   = idealIso <= iso;
                  const marginal = !viable && idealIso <= iso * 2;
                  const color    = viable ? "#6aaa70" : marginal ? "#b09040" : "#905030";
                  return (
                    <div key={fl} style={{
                      background: viable ? "#141e14" : marginal ? "#1a1a10" : "#1a1210",
                      border: `1px solid ${viable ? "#2a4a2a" : marginal ? "#3a3810" : "#2a1810"}`,
                      padding:"8px 10px", minWidth:58, textAlign:"center"
                    }}>
                      <div style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#8a8070", marginBottom:3}}>{fl}mm</div>
                      <div style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:11, color, fontWeight: viable ? 500 : 400}}>
                        {idealIso >= 10000 ? `${Math.round(idealIso/1000)}k` : idealIso}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div style={{marginTop:10, fontSize:10, fontFamily:"'IBM Plex Mono',monospace", color:"#8a8070"}}>
                <span style={{color:"#6aaa70"}}>●</span> viable at ISO {iso}{" · "}
                <span style={{color:"#b09040"}}>●</span> within 1 stop{" · "}
                <span style={{color:"#905030"}}>●</span> needs more ISO or OIS
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Lens list controls */}
      <div style={{display:"flex", gap:8, marginBottom:12, alignItems:"stretch", flexWrap:"wrap"}}>

        {/* Filter panel — landscape / architecture / street */}
        {(isLandscape || isStreet || isTravel || isPortrait || isSport || isWildlife) && (
          <div style={{display:"flex", alignItems:"center", gap:6, flexWrap:"wrap", flex:"2 1 320px",
            padding:"8px 12px", background:"#111", border:"1px solid #2a2520", borderRadius:4}}>
            <FilterDropdown label="Brand" multi selected={brandFilter} onChange={setBrandFilter}
              options={[...new Set(LENSES.filter(l=>l.format===(crop===0.79?"GFX":"X")).map(l=>l.brand))].sort().map(b=>({label:b,value:b}))} />
            <FilterDropdown label="Mark" multi selected={lsMarks} onChange={setLsMarks}
              options={[5,4,3,2,1].map(v=>({label:String(v),value:v}))} />
            {!isArchitecture && genre !== "Landscape" && <FilterDropdown label="Mode" multi selected={lsMode} onChange={setLsMode}
              options={["handheld","OIS/IBIS","tripod"].map(v=>({label:v,value:v}))} />}
            {!isArchitecture && <FilterDropdown label="Features" multi
              selected={[lsOis?"ois":null,lsWr?"wr":null].filter(Boolean)}
              onChange={v => { setLsOis(v.includes("ois")); setLsWr(v.includes("wr")); }}
              options={[{label:"OIS",value:"ois"},{label:"WR",value:"wr"}]} />}
            {isArchitecture && <FilterDropdown label="Features" multi
              selected={lsTs?["ts"]:[]}
              onChange={v => setLsTs(v.includes("ts"))}
              options={[{label:"T/S",value:"ts"}]} />}
            <FilterDropdown label="MTF" multi selected={mtfFilter} onChange={setMtfFilter}
              options={[10,9,8,7,6,5].map(v=>({label:String(v),value:v}))} />
            <FilterDropdown label="Weight ≤" multi={false} selected={lsWeight} onChange={setLsWeight}
              defaultValue={Infinity}
              options={[Infinity,0.2,0.3,0.5,0.8,1.5].map(v=>({label:v===Infinity?"Any":`${v}kg`,value:v}))} />
            <FilterDropdown label="Price" multi={false} selected={lsPrice} onChange={setLsPrice}
              defaultValue={Infinity}
              options={[Infinity,500,1000,2000,4000].map(v=>({label:v===Infinity?"Any":`€${v.toLocaleString()}`,value:v}))} />
            <button className="chip" onClick={() => {
              setBrandFilter([]); setMtfFilter([]); setLsMarks([]); setLsPrice(Infinity);
              setLsMode([]); setLsOis(false); setLsWr(false); setLsTs(false); setLsWeight(Infinity);
              setAoV(isArchitecture ? 12 : 24);
            }} style={{marginLeft:"auto", color:"#8a8070"}}>✕ clear</button>
          </div>
        )}

        {/* Sort panel removed — sorting via column headers */}

        {/* Filter panel — astro only */}
        {isAstro && (
          <div style={{display:"flex", alignItems:"center", gap:6, flexWrap:"wrap", flex:"2 1 320px",
            padding:"8px 12px", background:"#111", border:"1px solid #2a2520", borderRadius:4}}>
            <FilterDropdown label="Brand" multi selected={brandFilter} onChange={setBrandFilter}
              options={[...new Set((EV_LENSES.Astronomy||[]).map(l=>l.brand))].sort().map(b=>({label:b,value:b}))} />
            <FilterDropdown label="Mark" multi selected={astroMarks} onChange={setAstroMarks}
              options={[5,4,3,2,1].map(v=>({label:String(v),value:v}))} />
            <FilterDropdown label="MTF" multi selected={mtfFilter} onChange={setMtfFilter}
              options={[10,9,8,7,6,5].map(v=>({label:String(v),value:v}))} />
            <FilterDropdown label="Price" multi={false} selected={astroPrice} onChange={setAstroPrice}
              defaultValue={Infinity}
              options={[Infinity,500,1000,2000,4000].map(v=>({label:v===Infinity?"Any":`€${v.toLocaleString()}`,value:v}))} />
            <button className="chip" onClick={() => {
              setBrandFilter([]); setMtfFilter([]); setAstroMarks([]); setAstroPrice(Infinity);
            }} style={{marginLeft:"auto", color:"#8a8070"}}>✕ clear</button>
          </div>
        )}

      </div>

      {/* Results row */}
      <div style={{display:"flex", alignItems:"center", gap:8, marginBottom:6}}>
        <span className="count-badge">
          {lenses.filter(l=>!l._filtered).length} lenses
          {filteredCount > 0 ? isArchitecture ? ` · ${filteredCount} exposure >30s` : isLandscape ? ` · ${filteredCount} tripod only` : ` · ${filteredCount} need higher ISO` : ""}
        </span>
        {filteredCount > 0 && (
          <button className={`chip${showAll?" on":""}`} onClick={()=>setShowAll(!showAll)}>
            {showAll ? `hide ${filteredCount} filtered` : `show ${filteredCount} filtered`}
          </button>
        )}
      </div>

      {/* Lens list */}
      {isMobile ? (
        <div className="lens-cards">
          {lenses.length === 0 && (
            <div style={{padding:"24px", textAlign:"center", color:"#8a8070", fontFamily:"'IBM Plex Mono',monospace", fontSize:11}}>
              No lenses match the current filters.
            </div>
          )}
          {lenses.map((l, i) => {
            const suitability = (() => {
              if (isAstro) {
                const iso_ = l._astro?.idealIso;
                if (!iso_) return null;
                return iso_ <= iso ? { label:"viable", color:"#6aaa70", bg:"#141e14" }
                     : iso_ <= iso * 1.5 ? { label:"marginal", color:"#b09040", bg:"#1a1a10" }
                     : { label:"needs ISO", color:"#905030", bg:"#1a1210" };
              }
              const ref = isLandscape ? l._hh?.idealIsoRef : l._hh?.idealIso;
              if (!ref) return null;
              return ref <= iso     ? { label:"handheld",  color:"#6aaa70", bg:"#141e14" }
                   : ref <= iso * 8 ? { label:"OIS/IBIS",  color:"#e8a045", bg:"#1a1810" }
                   :                  { label:"tripod",     color:"#905030", bg:"#1a1210" };
            })();
            const fl  = l._astro?.fl ?? l._hh?.fl;
            const flFF = fl ? Math.round(fl * crop) : null;
            const ois = l._astro?.ois ?? l._hh?.ois;
            const wr  = l._astro?.wr  ?? l._hh?.wr;
            return (
              <div key={i} className={`lens-card${l.top && !l._filtered ? " top" : ""}${l._filtered ? " filtered" : ""}`}>
                <div className="lens-card-header">
                  <div>
                    <div className="lens-card-brand">{l.brand}</div>
                    <div className="lens-card-model">{l.model}</div>
                  </div>
                  {suitability && (
                    <span className="lens-card-mode" style={{color: suitability.color, background: suitability.bg}}>
                      {suitability.label}
                    </span>
                  )}
                </div>
                <div className="lens-card-row">
                  <div className="lens-card-fl">
                    {fl ? <>{fl}mm<span>· {flFF}mm FF</span></> : "–"}
                  </div>
                  <div className="lens-card-mtf"><MtfPips val={l.mtf} /></div>
                </div>
                <div className="lens-card-row">
                  <div className="lens-card-badges">
                    {ois && <span className="lens-card-badge" style={{background:"#1e1800", color:"#e8a045", border:"1px solid #3a3010"}}>OIS</span>}
                    {wr  && <span className="lens-card-badge" style={{background:"#1e1800", color:"#e8a045", border:"1px solid #3a3010"}}>WR</span>}
                  </div>
                  <div className="lens-card-price">{l.price ? `~€${l.price.toLocaleString()}` : "–"}</div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
      <table>
        <thead>
          <tr>
            {(() => {
              const S = (key, label, cls="") => {
                const active = sortBy === key;
                return (
                  <th className={cls} onClick={() => { sortBy===key ? setSortDir(d=>d*-1) : setSortBy(key); }}
                    style={{cursor:"pointer", userSelect:"none", whiteSpace:"nowrap",
                      color: active ? "#e8a045" : undefined}}>
                    {label}{active ? (sortDir===1 ? " ↑" : " ↓") : ""}
                  </th>
                );
              };
              return (<>
                {S("brand", "Brand")}
                {S("brand", "Model")}
                {hasMark && <th style={{textAlign:"center", cursor:"pointer", color: sortBy==="mark"?"#e8a045":undefined}}
                  onClick={()=>sortBy==="mark"?setSortDir(d=>d*-1):setSortBy("mark")}>
                  Mark{showOis?" (OIS)":""}{sortBy==="mark"?(sortDir===1?" ↑":" ↓"):""}
                </th>}
                {!isArchitecture && !isLandscape && S("iso", isAstro || isStreet || isTravel || isPortrait || isSport || isWildlife ? "Ideal ISO" : "Mode", "num")}
                {isArchitecture  && S("iso",   crop !== 0.79 ? "Min T @ f/8" : "Min T @ f/11", "num")}
                {!isAstro && !isArchitecture && <th style={{textAlign:"center"}}>WR</th>}
                {(isStreet || isTravel || isPortrait || isSport || isWildlife) && <th style={{textAlign:"center"}}>OIS</th>}
                {(isStreet || isTravel || isPortrait || isSport || isWildlife) && <th style={{textAlign:"center"}}>LM</th>}
                {isPortrait && <th style={{textAlign:"center"}}>APD</th>}
                {isArchitecture && <th style={{textAlign:"center"}}>T/S</th>}
                {S("fl",    "FL",    "num")}
                <th className="num">FL FF</th>
                {isAstro  && <th className="num">Rule 500</th>}
                {!isAstro && !isLandscape && <th className="num">1/FL</th>}
                {(isSport || isWildlife) && <th className="num">{isWildlife ? "Standoff" : "Dist"}</th>}
                {S("mtf",   "MTF",   "num")}
                {S("weight","kg",    "num")}
                {S("price", "€",     "num")}
              </>);
            })()}
          </tr>
        </thead>
        <tbody>
          {lenses.map((l, i) => {
            const m = (showOis && l.markOis != null) ? l.markOis : l.mark;
            return (
              <tr key={i} style={{
                opacity: l._filtered ? 0.4 : 1,
                background: l.top && !l._filtered ? "#0f0e0b" : "transparent"
              }}>
                <td className="brand">{l.brand}</td>
                <td className="model">{l.model}</td>
                {hasMark && (
                  <td style={{textAlign:"center"}}><MarkDots mark={m} /></td>
                )}
                {!isLandscape && (() => {
                  const idealIso = l._astro?.idealIso ?? l._hh?.idealIso;
                  if (!idealIso) return <td className="num" style={{color:"#8a8070"}}>–</td>;
                  if (isAstro || isStreet || isTravel || isPortrait || isSport || isWildlife) {
                    const color = idealIso <= iso       ? "#6aaa70"
                                : idealIso <= iso * 1.5 ? "#b09040"
                                :                        "#905030";
                    return <td className="num" style={{color, fontWeight: idealIso <= iso ? 500 : 400}}>{idealIso}</td>;
                  }
                  const cat   = idealIso <= iso     ? "handheld"
                              : idealIso <= iso * 8  ? "OIS/IBIS"
                              :                        "tripod";
                  const color = cat === "handheld" ? "#6aaa70" : cat === "OIS/IBIS" ? "#e8a045" : "#905030";
                  return <td className="num" style={{color, fontWeight: cat === "handheld" ? 500 : 400}}>{cat}</td>;
                })()}
                {isArchitecture && (() => {
                  const fl      = l._hh?.fl;
                  const tripodT = (sweetSpot * sweetSpot * 100) / (iso * Math.pow(2, ev)) * ndFactor;
                  const t           = tripodT;
                  const sharpThresh = 1/60;
                  const color = t <= sharpThresh ? "#4090d0"
                              : t <= 30         ? "#d06040"
                              :                   "#40d0b0";
                  const label = t < 1
                    ? `1/${Math.round(1/t)}s`
                    : t < 60
                    ? `${Math.round(t)}s`
                    : `${Math.round(t/60)}min`;
                  return <td className="num" style={{color, fontWeight: t <= sharpThresh ? 500 : 400}}>{label}</td>;
                })()}
                {!isAstro && !isArchitecture && <td style={{textAlign:"center", fontFamily:"'IBM Plex Mono',monospace", fontSize:10,
                  color: l._hh?.wr ? "#e8a045" : "#4a4540"}}>
                  {l._hh?.wr ? "WR" : "–"}
                </td>}
                {(isStreet || isTravel || isPortrait || isSport || isWildlife) && <td style={{textAlign:"center", fontFamily:"'IBM Plex Mono',monospace", fontSize:10,
                  color: l._hh?.ois ? "#e8a045" : "#4a4540"}}>
                  {l._hh?.ois ? "OIS" : "–"}
                </td>}
                {(isStreet || isTravel || isPortrait || isSport || isWildlife) && (() => {
                  const hasLM = l.model.toUpperCase().includes(" LM");
                  return <td style={{textAlign:"center", fontFamily:"'IBM Plex Mono',monospace", fontSize:10,
                    color: hasLM ? "#e8a045" : "#4a4540"}}>
                    {hasLM ? "LM" : "–"}
                  </td>;
                })()}
                {isPortrait && (() => {
                  const hasAPD = l.model.toUpperCase().includes("APD");
                  return <td style={{textAlign:"center", fontFamily:"'IBM Plex Mono',monospace", fontSize:10,
                    color: hasAPD ? "#e8a045" : "#4a4540"}}>
                    {hasAPD ? "APD" : "–"}
                  </td>;
                })()}
                {isArchitecture && (() => {
                  const isTS = l.model.includes("T/S") || l.model.toLowerCase().includes("tilt") || l.model.toLowerCase().includes("shift");
                  return <td style={{textAlign:"center", fontFamily:"'IBM Plex Mono',monospace", fontSize:10,
                    color: isTS ? "#e8a045" : "#4a4540", fontWeight: isTS ? 500 : 400}}>
                    {isTS ? "T/S" : "–"}
                  </td>;
                })()}
                {isAstro && <td className="num" style={{color:"#b0a898"}}>{l._astro ? `${l._astro.fl}mm` : "–"}</td>}
                {isAstro && <td className="num" style={{color:"#8a8070"}}>{l._astro ? `${Math.round(l._astro.fl * crop)}mm` : "–"}</td>}
                {!isAstro && <td className="num" style={{color:"#b0a898"}}>{l._hh ? `${l._hh.fl}mm` : "–"}</td>}
                {!isAstro && <td className="num" style={{color:"#8a8070"}}>{l._hh ? `${Math.round(l._hh.fl * crop)}mm` : "–"}</td>}
                {isAstro && <td className="num" style={{color:"#8a8070"}}>{l._astro ? `${Math.round(l._astro.maxT)}s` : "–"}</td>}
                {!isAstro && !isLandscape && <td className="num" style={{color:"#8a8070"}}>{l._hh ? `1/${Math.round(1/l._hh.minShutter)}` : "–"}</td>}
                {(isSport || isWildlife) && (() => {
                  if (!l._hh) return <td className="num" style={{color:"#8a8070"}}>–</td>;
                  if (isSport) return <td className="num" style={{color:"#b0a898"}}>{Math.round(l._hh.fl/10)}m</td>;
                  const standoff = Math.round(l._hh.fl * wildlifeSubject.size / 15.6);
                  return <td className="num" style={{color:"#b0a898"}}>{standoff}m</td>;
                })()}
                <td className="num"><MtfPips val={l.mtf} /></td>
                <td className="num" style={{color:"#b0a898"}}>{l.kg != null ? `${l.kg}kg` : "–"}</td>
                <td className="num price">{l.price ? `~${l.price.toLocaleString()}` : "–"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      )}
    </div>
  );
}

// ─── WIKI ─────────────────────────────────────────────────────────────────────
const WIKI = [
  {short:"Active AF",   full:"Active Autofocus",         cat:"Focus",       info:"AF category where the camera emits energy (light or sound) and measures the reflection to determine distance to the subject. Works in complete darkness and on low-contrast subjects. Range is limited and can be fooled by glass. Used as AF-assist in some cameras."},
  {short:"AF-C",        full:"Continuous AF",            acro:true, cat:"Focus",       info:"Camera continuously adjusts focus while the shutter is held half-pressed, tracking moving subjects. Essential for sport and wildlife. Fuji X-series AF-C uses PDAF only within PDAF coverage zones."},
  {short:"AF-S",        full:"Single AF",                acro:true, cat:"Focus",       info:"Camera focuses once, then locks. Best for stationary subjects. Typically uses hybrid CDAF/PDAF for accuracy. See Focus modes sheet for Fuji-specific behaviour by focus point type."},
  {short:"Aliasing",    full:"Aliasing",          cat:"Optics",      info:"Artefact caused when the sensor resolution is insufficient to capture fine detail, resulting in moiré patterns or stair-stepping on diagonal lines. Prevented by anti-aliasing filters."},
  {short:"Angular resolution", full:"Angular Resolution", cat:"Optics", info:"The minimum angle between two point sources that a system can resolve as distinct. For a camera: limited by both the diffraction limit (aperture) and sensor pixel pitch. Determines effective resolving power at a given distance."},
  {short:"Anti-aliasing", full:"", cat:"Optics", info:"An optical low-pass filter placed in front of the sensor that slightly blurs the image to prevent aliasing artefacts. Reduces sharpness marginally; many modern cameras omit it."},
  {short:"Anti-Reflective Coating", full:"", cat:"Optics", info:"A specific type of lens coating that minimises light reflection at glass-air interfaces. Without it, each lens element reflects ~4% of light, causing flare and contrast loss."},
  {short:"AoV",    full:"Angle of View",         acro:true, cat:"Geometry",    info:"The angular extent of the scene captured by a lens, measured diagonally, horizontally or vertically. Wider AoV = wider lens. Determined by focal length and sensor size."},
  {short:"APD",    full:"Apodization Filter",           acro:true, cat:"Lenses",    info:"A radial neutral-density filter built into the lens that gradually reduces light transmission towards the outer aperture zone. Smooths bokeh by eliminating the hard edge of the aperture disc. Used in the Fujifilm XF 56mm f/1.2 APD. Causes ~1 stop light loss."},
  {short:"Aperture", full:"Aperture",             cat:"Exposure",    info:"The opening in the lens that controls light transmission. Expressed as f-number (f/2.8, f/8). Wider aperture (lower f-number) = more light, shallower DoF, faster shutter possible."},
  {short:"Aperture Ring",      full:"",                cat:"Lenses",    info:"A physical ring on the lens barrel that controls the aperture directly, independent of camera dials. XF lenses marked 'R' feature an aperture ring with click stops at each f-stop. Preferred by photographers who want tactile aperture control without diving into menus."},
  {short:"Aperture Sweet Spot", full:"",     cat:"Exposure",  info:"The aperture at which a lens delivers peak sharpness across the frame, typically 2–3 stops below maximum aperture. For APS-C the sweet spot is f/5.6–f/8 — the lower end applies to high-resolution bodies (40MP+) where diffraction becomes visible earlier. Stopping down further reduces sharpness due to diffraction."},
  {short:"APS-C",  full:"Advanced Photo System type-C", acro:true, cat:"Sensor", info:"A sensor format measuring approximately 23.5×15.6mm, with a crop factor of 1.5× (Fujifilm). Smaller and lighter than full-frame but captures less light per pixel at equivalent aperture."},
  {short:"Beauty dish",   full:"",                    cat:"Lighting",    info:"A circular modifier with a central deflector that produces a distinctive quality of light — softer than bare flash but harder than a softbox. Creates a characteristic ring catchlight. Widely used for portrait and fashion photography."},
  {short:"Bokeh", full:"Bokeh",                   cat:"Optics",      info:"The aesthetic quality of the out-of-focus areas in an image. Determined by aperture shape, lens design, and aberrations. Smooth, circular bokeh is generally considered pleasing; 'nervous' bokeh has hard edges."},
  {short:"Brenizer method", full:"Brenizer Method", cat:"Composition", info:"Technique pioneered by Ryan Brenizer: shoot a subject at wide aperture with a telephoto lens, then stitch multiple images into a panoramic frame. Produces a field of view resembling a wide lens but with the extremely shallow DoF of a fast telephoto."},
  {short:"CDAF",        full:"Contrast Detection AF  [Passive]",  acro:true, cat:"Focus", info:"Moves the lens in small steps and measures contrast at each position; stops when contrast peaks. Accurate but slow — must overshoot and return to find the maximum. Best for static subjects and video. Used as fallback in Fuji X-series when PDAF is unavailable."},
  {short:"Colour harmony",       full:"",              cat:"Composition", info:"Intentional use of colour relationships to create mood: complementary colours (opposite on the colour wheel, e.g. orange/blue) create energy; analogous colours (adjacent, e.g. green/teal/blue) create calm and cohesion."},
  {short:"Colour temperature", full:"",               cat:"Lighting",    info:"The warmth or coolness of a light source, measured in Kelvin (K). Candle ~1800K, tungsten ~3200K, daylight ~5500K, open shade ~7000K. Affects white balance — cooler light appears blue, warmer light appears orange."},
  {short:"CRI",           full:"Colour Rendering Index", acro:true, cat:"Lighting", info:"A scale (0–100) measuring how accurately a light source renders colours compared to natural sunlight. CRI 90+ is excellent for photography. Low CRI lights cause colours to appear muddy or shifted."},
  {short:"Crop factor", full:"Crop Factor",       cat:"Geometry",    info:"Ratio of a sensor's diagonal to that of full-frame (36×24mm). APS-C crop = 1.5×, GFX = 0.79×. Multiply FL by crop factor to get the full-frame equivalent."},
  {short:"Deblurring",  full:"Deblurring",        cat:"Optics",      info:"Post-processing technique to recover sharpness from motion blur or defocus blur. Modern AI deblurring (e.g. Lightroom AI Sharpening) can recover surprising detail but cannot exceed the sensor's Nyquist limit."},
  {short:"Deconvolution", full:"Deconvolution",   cat:"Optics",      info:"Mathematical process to reverse the blurring effect of a known optical system (PSF). Used in microscopy and astrophotography to recover fine detail. Prone to amplifying noise."},
  {short:"Depth",                full:"Depth and Layers", cat:"Composition", info:"Including a foreground, mid-ground, and background creates a sense of three-dimensional space in a flat image. Wide-angle lenses exaggerate depth; objects in the foreground draw the eye in and provide scale."},
  {short:"DFD",         full:"Depth-From-Defocus  [Passive]",     acro:true, cat:"Focus", info:"Estimates defocus amount by comparing two images captured at different aperture diameters, using the known relationship between defocus blur size and depth. Developed by Panasonic. Faster than pure CDAF but not as predictive as PDAF. Not used in Fuji systems."},
  {short:"Diffraction", full:"Diffraction",       cat:"Optics",      info:"At small apertures (f/11+), light bends around the aperture blades, causing softness regardless of lens quality. The diffraction limit for APS-C is approximately f/11; for GFX, f/16."},
  {short:"Diffraction-limited system", full:"Diffraction-Limited System", cat:"Optics", info:"An optical system where performance is limited by diffraction rather than aberrations or manufacturing imperfections. Represents the theoretical maximum sharpness for a given aperture."},
  {short:"Diffuser",      full:"",                    cat:"Lighting",    info:"Any material that scatters light to make it softer and more even. Can be a softbox panel, a translucent umbrella, a dome on a speedlight, or a large white sheet. The larger the diffuser relative to the subject, the softer the light."},
  {short:"DoF",    full:"Depth of Field",         acro:true, cat:"Geometry",    info:"The range of distances in a scene that appear acceptably sharp. Controlled by aperture (wider = shallower DoF), focal length, and subject distance."},
  {short:"Dynamic dimensions", full:"Dynamic Dimensions", cat:"Composition", info:"The use of strong leading lines, diagonals, and converging perspectives to create a sense of movement, depth or tension in a static image. Contrasts with static, symmetrical compositions."},
  {short:"EV",     full:"Exposure Value",         acro:true, cat:"Exposure",    info:"A single number representing a combination of shutter speed and aperture that produces the same exposure. EV 0 = 1s at f/1. Each stop doubles or halves the exposure. EV 15 = bright sun."},
  {short:"f-Value", full:"f-Number (f-Stop)",     cat:"Exposure",    info:"The ratio of focal length to aperture diameter. f/2.8 on a 50mm lens means the aperture is 50/2.8 = 17.9mm wide. Each full stop (f/2.8→f/4) halves the light."},
  {short:"Fill the frame",       full:"",              cat:"Composition", info:"Getting close to the subject so it occupies most or all of the frame, eliminating distracting backgrounds. Creates intimacy and impact. Particularly effective for portraits, textures, and details."},
  {short:"FL",     full:"Focal Length",           acro:true, cat:"Geometry",    info:"Distance in mm from the optical centre of the lens to the focal point on the sensor. Determines magnification and angle of view. Shorter = wider, longer = more telephoto."},
  {short:"FL FF",  full:"Focal Length Full-Frame Equivalent", acro:true, cat:"Geometry", info:"The focal length on a full-frame camera that produces the same angle of view. For APS-C: FL FF = FL × 1.5. Useful for comparing lenses across sensor formats."},
  {short:"Flash",         full:"",                    cat:"Lighting",    info:"A brief, intense burst of artificial light used to illuminate a scene. Can be on-camera (hotshoe), off-camera (remote triggered), or built-in. Power is measured in watt-seconds (Ws) for studio units or guide number (GN) for speedlights."},
  {short:"Foreground interest",  full:"",              cat:"Composition", info:"Placing a visually interesting element in the immediate foreground to anchor the composition and create depth. Particularly important in landscape photography where a strong foreground transforms an ordinary scene into a compelling image."},
  {short:"FoV",    full:"Field of View",          acro:true, cat:"Geometry",    info:"The physical area of a scene captured at a given distance. Unlike AoV (angular), FoV is expressed in metres. FoV grows proportionally with distance."},
  {short:"Framing",              full:"",              cat:"Composition", info:"Using elements within the scene (doorways, arches, foliage, windows) to form a natural frame around the subject. Draws attention to the subject, adds depth, and provides context about the environment."},
  {short:"Fresnel Lens",       full:"",        cat:"Lighting",    info:"A stepped focusing lens placed in front of a light source to concentrate and shape the beam. Used on studio heads and LED panels to produce a hard, directional, focusable light — adjustable from flood to spot."},
  {short:"Full-frame", full:"Full-Frame",          cat:"Sensor",      info:"Sensor size matching 35mm film: 36×24mm, crop factor 1.0×. Larger photosites capture more light, yielding better dynamic range and high-ISO performance than smaller formats."},
  {short:"G-Mount", full:"", cat:"Lenses", info:"Fujifilm's lens mount for the GFX medium format system. Larger than X-Mount to accommodate the bigger sensor. GF lenses are not compatible with X-Mount bodies. The mount supports tilt-shift lenses and features a wide flange distance for optical quality."},
  {short:"Gamma correction", full:"Gamma Correction", cat:"Optics",  info:"A nonlinear tone mapping applied to image data to match human perception of brightness. Camera sensors capture linear light; gamma encoding (e.g. sRGB γ=2.2) compresses highlights and expands shadows."},
  {short:"GFX / Medium Format", full:"GFX / Medium Format", acro:true, cat:"Sensor", info:"Fujifilm's medium format system uses a 43.8×32.9mm sensor, crop factor 0.79×. Larger than full-frame, producing extremely high resolution (up to 102MP) and exceptional tonal gradation."},
  {short:"Golden ratio",   full:"Golden Ratio",    cat:"Composition", info:"Mathematical ratio ≈1.618:1 (φ, phi) found throughout nature and classical art. Used as a compositional guide: placing subjects at golden ratio intersections or along spiral curves creates naturally pleasing images."},
  {short:"Golden rectangle", full:"Golden Rectangle", cat:"Composition", info:"A rectangle whose sides are in the golden ratio (1:1.618). Subdividing it repeatedly produces a logarithmic spiral used in the Fibonacci/golden spiral compositional guide."},
  {short:"Guide number",  full:"",                    cat:"Lighting",    info:"A standardised measure of flash power: GN = distance × f-number (at ISO 100). A GN of 60 means at 6m you need f/10, or at 3m you need f/20. Higher GN = more powerful flash."},
  {short:"Handheld", full:"Handheld Shooting",        cat:"Exposure",   info:"Shooting without a tripod or other support. Subject to camera shake, which sets a minimum shutter speed determined by focal length, stabilisation, and sensor resolution. The reciprocal rule (1/FL) is the standard guideline."},
  {short:"Honeycomb Grid",          full:"",      cat:"Lighting",    info:"A honeycomb-shaped attachment that fits over a modifier to control light spill and keep illumination directional. Measured in degrees (10°, 20°, 40°) — tighter grids produce more controlled beams."},
  {short:"HSS",           full:"High Speed Sync",     acro:true, cat:"Lighting",    info:"Allows flash to be used at shutter speeds above the camera sync speed (typically 1/250s). The flash fires multiple rapid pulses throughout the exposure. Trades power for speed — useful for outdoor portraits at wide aperture in bright light."},
  {short:"Hybrid AF",   full:"Hybrid AF  [Passive]",              cat:"Focus", info:"Combines PDAF (for speed and direction) with CDAF (for final accuracy). The camera uses PDAF to get close, then switches to CDAF for precise confirmation. Used in virtually all modern Fuji X-series bodies."},
  {short:"IBIS",   full:"In-Body Image Stabilisation", acro:true, cat:"Sensor",  info:"Sensor-shift stabilisation built into the camera body. Works with any lens, including manual and adapted lenses without optical stabilisation. Fuji X-H2, X-H2S, X-T4, and X-T5 feature IBIS. Combined OIS+IBIS can provide up to 7 stops of compensation."},
  {short:"Image resolution", full:"Image Resolution", cat:"Optics",  info:"The number of pixels in a captured image, typically expressed as megapixels (MP) or as width × height (e.g. 7728×5152). Higher resolution enables larger prints and more crop flexibility."},
  {short:"Integrating sphere", full:"Integrating Sphere", cat:"Optics", info:"A hollow sphere with diffuse white interior coating used to measure total luminous flux from a light source. Used in lens and sensor calibration laboratories."},
  {short:"IR AF",       full:"IR Beam AF  [Active]",                cat:"Focus", info:"Emits an infrared beam and measures the angle or time-of-flight of the reflection to determine distance. Used as AF-assist illuminators in some cameras and dedicated video follow-focus systems. Limited range (~5m)."},
  {short:"ISO",    full:"ISO Sensitivity",        acro:true, cat:"Exposure",    info:"The sensor's amplification of the captured light signal. Higher ISO = brighter image in low light but more noise. Base ISO (typically 100–200) gives cleanest results."},
  {short:"Leading lines",        full:"",              cat:"Composition", info:"Lines within the scene (roads, rivers, fences, shadows) that draw the viewer's eye towards the main subject or deeper into the frame. Most effective when they originate from a corner and converge toward the subject."},
  {short:"LED panel",     full:"LED Continuous Light", cat:"Lighting",   info:"A continuous (always-on) light source using LEDs. Unlike flash, it allows real-time preview of lighting. Useful for video. Modern bi-colour LED panels adjust from tungsten (3200K) to daylight (5600K)."},
  {short:"Lens Coating",     full:"",      cat:"Optics",      info:"Multi-layer anti-reflective coatings applied to lens elements to reduce flare, ghosting, and light loss. High-quality coatings (e.g. Fuji EBC, Zeiss T*) significantly improve contrast in backlit situations."},
  {short:"LiDAR AF",    full:"LiDAR AF  [Active]",                  cat:"Focus", info:"Emits pulsed laser light and measures the time-of-flight of the reflection with high precision. Used in iPhone Pro (camera app depth assist) and some cinema accessories. Not used in Fuji stills cameras."},
  {short:"Lighting Umbrella", full:"",     cat:"Lighting",    info:"A modifier used with flash or studio lights. Shoot-through umbrellas diffuse light for a soft source; reflective umbrellas redirect light for a larger, directional source. Portable and inexpensive."},
  {short:"LM",          full:"Linear Motor (actuator)",  acro:true, cat:"Focus",       info:"A lens AF actuator using a linear electromagnetic motor rather than a traditional rotating motor. Provides faster, quieter, and more accurate focus tracking. Not an AF detection method — pairs with any of the above. Critical for sport and wildlife photography."},
  {short:"Macro",  full:"Macro Photography",            cat:"Lenses",    info:"Close-up photography at reproduction ratios of 1:1 (life-size) or greater. A true macro lens focuses close enough to project a 1:1 image on the sensor — a 10mm insect fills 10mm of the sensor. Fuji XF 80mm f/2.8 and XF 30mm f/2.8 are native macro lenses."},
  {short:"Metering", full:"Metering",             cat:"Exposure",    info:"The camera's system for measuring scene brightness to determine exposure. Modes include evaluative/matrix (whole scene), spot (small area), and centre-weighted."},
  {short:"Moiré pattern", full:"Moiré Pattern",   cat:"Optics",      info:"An interference pattern that appears when two regular patterns (e.g. fine fabric texture and sensor grid) overlap at similar frequencies. Reduced by anti-aliasing filters."},
  {short:"MRC",    full:"Minimum Resolvable Contrast", acro:true, cat:"Optics",  info:"The lowest contrast level that a lens or imaging system can still resolve as distinct detail. Related to MTF at high spatial frequencies."},
  {short:"MTF",    full:"Modulation Transfer Function", acro:true, cat:"Optics", info:"A measure of a lens's ability to reproduce fine detail and contrast. Plotted as a curve: higher values across spatial frequencies = sharper, higher contrast image. The gold standard for lens testing."},
  {short:"ND",     full:"Neutral Density Filter",      acro:true, cat:"Exposure",  info:"A filter that reduces light entering the lens without affecting colour balance. Allows slower shutter speeds (silk water, light trails) or wider apertures (shallower DoF) in bright conditions. Expressed in stops (ND2=1 stop, ND8=3 stops, ND64=6 stops, ND1000=10 stops)."},
  {short:"Negative space", full:"Negative Space",  cat:"Composition", info:"The empty or unoccupied area surrounding the main subject. Effective use of negative space creates breathing room, emphasises the subject, and conveys mood. Often seen in minimalist photography."},
  {short:"OIS",    full:"Optical Image Stabilisation", acro:true, cat:"Lenses",    info:"In-lens mechanism that shifts optical elements to compensate for camera shake. Measured in EV stops of compensation. Particularly valuable at long focal lengths and slow shutter speeds. Fuji XF lenses mark OIS-equipped models explicitly."},
  {short:"Optical resolution", full:"Optical Resolution", cat:"Optics", info:"The true resolving power of a lens, independent of sensor resolution. Expressed as line pairs per millimetre (lp/mm). A lens must exceed the sensor's Nyquist frequency to avoid resolution bottleneck."},
  {short:"Oversampling", full:"Oversampling",     cat:"Optics",      info:"Capturing at higher resolution than needed and downsampling. Improves effective sharpness and reduces noise. Used in video modes (e.g. Fuji X-T5 shoots 40MP to produce oversampled 8K video)."},
  {short:"Panning", full:"Panning",                   cat:"Exposure",   info:"Technique of tracking a moving subject with the camera during a relatively slow exposure. The subject appears sharp while the background streaks horizontally. Requires a shutter speed slow enough to create motion blur in the background, typically 1/30–1/125s depending on subject speed."},
  {short:"Passive AF",  full:"Passive Autofocus",        cat:"Focus",       info:"AF category that analyses the incoming image itself to determine focus — no light is emitted by the camera. All methods below (CDAF, PDAF, Hybrid, DFD) are passive. Works in any lighting where there is enough contrast or phase information in the scene."},
  {short:"Patterns and texture", full:"",              cat:"Composition", info:"Repeating shapes, lines, or textures create rhythm and visual interest. Breaking a pattern with a single different element (pattern interrupt) immediately draws the eye. Textures are best revealed by side-lighting."},
  {short:"PDAF",        full:"Phase Detection AF  [Passive]",     acro:true, cat:"Focus", info:"Dedicated pixel pairs on the sensor receive light from slightly different angles; the phase difference between them reveals the direction and magnitude of defocus. Fast, predictive, and does not need to hunt. Used in Fuji X-series within PDAF coverage zones. Performance degrades above f/8."},
  {short:"Point of view",        full:"",              cat:"Composition", info:"The physical relationship between photographer, subject, and background. Shooting at eye-level with children or animals creates connection; shooting from above creates distance. Changing point of view is the single most impactful compositional decision."},
  {short:"Reciprocal Rule", full:"",          acro:true, cat:"Exposure",  info:"The minimum handheld shutter speed to avoid camera-shake blur equals 1 divided by the focal length. For a 50mm lens on APS-C: minimum shutter = 1/(50×1.5) = 1/75s. High-resolution sensors require a stricter version: 1/(√(MP/12) × crop × FL)."},
  {short:"Reflector", full:"Reflector",            cat:"Lighting",    info:"A surface used to redirect ambient or artificial light onto a subject. White = soft fill, silver = brighter harder fill, gold = warm fill. Used to reduce contrast in portrait and product photography."},
  {short:"Rule of 500", full:"Rule of 500 (Astrophotography)", acro:true, cat:"Exposure", info:"Maximum untracked exposure time before stars trail: 500 ÷ (crop factor × focal length). For a 16mm lens on APS-C (crop 1.5): 500 ÷ (1.5 × 16) = 20 seconds. A stricter version using 300 is preferred for high-resolution sensors."},
  {short:"Rule of odds",         full:"",              cat:"Composition", info:"Groups of odd numbers of subjects (3, 5, 7) are more visually pleasing than even groups. An odd number creates a natural focal point — one subject stands out. Particularly useful in product and food photography."},
  {short:"Rule of thirds",      full:"",              cat:"Composition", info:"Divide the frame into a 3×3 grid; place key subjects or horizon lines along the grid lines or at their intersections (power points). Creates more dynamic, balanced compositions than centring the subject. The most fundamental compositional guideline in photography."},
  {short:"S-curve",              full:"S-Curve",       cat:"Composition", info:"A flowing S-shaped curve (rivers, roads, staircases) that leads the eye gracefully through the frame. More dynamic than a straight leading line; conveys elegance and movement. Common in landscape and portrait photography."},
  {short:"Siemens star", full:"Siemens Star",     cat:"Optics",      info:"A test chart consisting of alternating black and white wedges radiating from a centre point. Used to measure resolving power and detect astigmatism or other aberrations at different field positions."},
  {short:"Simplicity",           full:"",              cat:"Composition", info:"Reducing the scene to its essential elements by choosing a clean background, isolating the subject, or finding an uncluttered angle. Minimalist compositions are often the most powerful. 'If in doubt, take it out.'"},
  {short:"SiTF",   full:"Signal Transfer Function", acro:true, cat:"Optics",    info:"Describes how a sensor or imaging system converts scene radiance to output signal. Used in scientific imaging to characterise linearity and dynamic range."},
  {short:"Snoot",         full:"",                    cat:"Lighting",    info:"A cone or tube attached to a flash or studio head to narrow the light beam to a small spot. Used to isolate subjects, light hair, or create dramatic accent lighting without spill."},
  {short:"SNR",    full:"Signal-to-Noise Ratio",  acro:true, cat:"Optics",      info:"Ratio of the useful image signal to background noise. Higher SNR = cleaner image. Decreases at high ISO. Larger sensor pixels generally produce better SNR."},
  {short:"Softbox",       full:"",                    cat:"Lighting",    info:"A box-shaped modifier that diffuses light through a translucent panel, producing soft, even illumination with gentle shadow transitions. Size determines softness — larger = softer. Common shapes: rectangular, octabox, strip."},
  {short:"Speedlight",    full:"",                    cat:"Lighting",    info:"A portable battery-powered flash unit that mounts on the camera hotshoe or is used off-camera. Less powerful than studio strobes but highly portable. Supports TTL and HSS on compatible cameras."},
  {short:"Strehl ratio", full:"Strehl Ratio",     cat:"Optics",      info:"A measure of optical quality comparing peak intensity of an aberrated system to a perfect diffraction-limited system. Value of 1.0 = perfect. Values above 0.8 are considered diffraction-limited."},
  {short:"Studio Strobe",        full:"",       cat:"Lighting",    info:"A powerful mains-powered flash unit used in studio settings. Significantly more powerful than speedlights (100–1000+ Ws). Usually includes a modelling lamp to preview light direction before shooting."},
  {short:"Super-resolution imaging", full:"Super-Resolution Imaging", cat:"Optics", info:"Techniques to produce images with resolution beyond the sensor's native limit. In-camera pixel shift (e.g. Fuji Pixel Shift Multi-Shot) combines multiple exposures; AI upscaling uses neural networks."},
  {short:"Superlens",   full:"Superlens",         cat:"Optics",      info:"A theoretical or experimental optical device using metamaterials with negative refractive index to overcome the diffraction limit. Not yet practical for photography."},
  {short:"Symmetry",             full:"",              cat:"Composition", info:"Placing the subject centrally to exploit mirror-like reflections or architectural symmetry. Breaks the rule of thirds intentionally to create a sense of balance, calm, and formality. Most effective with strong reflections or geometric patterns."},
  {short:"TC",     full:"Tele Converter",               acro:true, cat:"Lenses",    info:"An optical accessory placed between camera body and lens to multiply focal length. Fujifilm XF 1.4× TC WR and XF 2.0× TC WR are compatible with select XF lenses. The 1.4× costs 1 stop of light; the 2.0× costs 2 stops. AF performance is maintained on compatible lenses."},
  {short:"Tilt-Shift",    full:"",                  acro:true, cat:"Lenses",    info:"A lens with mechanical movements allowing the optical axis to be tilted (controls plane of focus) or shifted (corrects perspective distortion). Used in architecture to keep vertical lines parallel. Fujifilm offers GF 30mm f/5.6 T/S and GF 110mm f/5.6 T/S Macro."},
  {short:"TTL",           full:"Through The Lens metering", acro:true, cat:"Lighting", info:"Automatic flash exposure system where the camera meters light through the lens and adjusts flash power accordingly. Fires a pre-flash to measure the scene, then sets the main flash power. Convenient but can be fooled by reflective or dark subjects."},
  {short:"Ulbricht sphere", full:"Ulbricht Sphere", cat:"Optics",    info:"Another name for an integrating sphere, named after German physicist Ulbricht. Used to achieve spatially uniform illumination for radiometric measurements."},
  {short:"Viewpoint",            full:"",              cat:"Composition", info:"The position and angle from which a photo is taken dramatically changes its meaning. Low angles make subjects imposing; high angles create vulnerability or show patterns. Moving just a metre can transform a cluttered scene into a clean composition."},
  {short:"WR",     full:"Weather Resistance",           acro:true, cat:"Lenses",    info:"Sealing at lens barrel joints and focus ring to resist dust and moisture ingress. WR lenses require a WR camera body for full protection. Essential for outdoor sport, wildlife, and landscape work in variable conditions."},
  {short:"X-Mount", full:"", cat:"Lenses", info:"Fujifilm's mirrorless interchangeable lens mount for the X-series APS-C system. Short 17.7mm flange distance allows compact lens designs. Compatible with XF and XC lenses. Not compatible with GFX / G-Mount lenses."},
  {short:"XC",     full:"XC Lens Series",              acro:true, cat:"Lenses", info:"Fujifilm's budget X-Mount lens series. Plastic mount, no weather resistance, lighter and more compact than XF equivalents. Designed for entry-level X-series bodies. The XC 15-45mm, 16-50mm, 35mm f/2, and 50-230mm are the main examples."},
  {short:"XF",     full:"XF Lens Series",              acro:true, cat:"Lenses", info:"Fujifilm's main X-Mount lens lineup. Covers professional primes and zooms with consistent quality, weather-resistant options, and linear motor variants. Designed for the full X-series camera range."},
];

function GlossaryView() {
  const [search, setSearch] = useState("");
  const [activeCat, setActiveCat] = useState("All");
  const cats = ["All", ...new Set(WIKI.map(g => g.cat))];
  const filtered = WIKI.filter(g =>
    (activeCat === "All" || g.cat === activeCat) &&
    (search === "" || g.short.toLowerCase().includes(search.toLowerCase()) || g.full.toLowerCase().includes(search.toLowerCase()) || g.info.toLowerCase().includes(search.toLowerCase()))
  );
  return (
    <div>
      {/* Header + search */}
      <div style={{display:"flex", gap:10, alignItems:"center", marginBottom:14, flexWrap:"wrap"}}>
        <input
          value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Search…"
          style={{background:"#111", border:"1px solid #2a2520", color:"#e0d8cc", padding:"5px 10px",
            fontFamily:"'IBM Plex Mono',monospace", fontSize:11, outline:"none", width:200}}
        />
        <div style={{display:"flex", gap:4, flexWrap:"wrap"}}>
          {cats.map(c => (
            <button key={c} className={`chip${activeCat===c?" on":""}`}
              onClick={() => setActiveCat(c)} style={{padding:"2px 8px"}}>{c}</button>
          ))}
        </div>
        <span style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#4a4540", marginLeft:"auto"}}>
          {filtered.length} / {WIKI.length} terms
        </span>
      </div>

      {/* Terms grid */}
      <div style={{display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(320px, 1fr))", gap:10}}>
        {filtered.map(({short, full, cat, info, acro}) => (
          <div key={short} style={{background:"#0f0d0b", border:"1px solid #1e1b16", padding:"10px 14px"}}>
            <div style={{display:"flex", alignItems:"baseline", gap:8, marginBottom:4}}>
              <span style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:13, color:"#e8a045", fontWeight:700}}>{short}</span>
              {acro && full && <span style={{fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#b0a898"}}>{full}</span>}
              <span style={{marginLeft:"auto", fontFamily:"'IBM Plex Mono',monospace", fontSize:9, color:"#8a8070",
                textTransform:"uppercase", letterSpacing:"0.06em", background:"#1a1816", padding:"1px 6px"}}>{cat}</span>
            </div>
            <div style={{fontFamily:"system-ui, sans-serif", fontSize:12, color:"#7a7268", lineHeight:1.6}}>
              {info}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── ACCESSORIES ──────────────────────────────────────────────────────────────
const ACCESSORIES = [
  // Flash
  {cat:"Flash",        model:"EF-X500",     desc:"Top-tier TTL flash. GN50, FP high-speed sync, wireless commander/remote. Accepts EF-BP1 battery pack.", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S, X-E1/2/3/4, X-S10/20, X-A/M series, GFX"},
  {cat:"Flash",        model:"EF-60",        desc:"Radio-controlled wireless TTL flash. GN60, first Fuji flash with built-in radio receiver. Works with EF-W1.", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S, X-E1/2/3/4, X-S10/20, X-A/M series, GFX"},
  {cat:"Flash",        model:"EF-42",        desc:"Mid-range TTL/manual flash. GN42, shoe-mount. Good travel companion.", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S, X-E1/2/3/4, X-S10/20, X-A/M series"},
  {cat:"Flash",        model:"EF-X20",       desc:"Compact TTL flash. GN20, lightweight. Minimal footprint.", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S, X-E1/2/3/4, X-S10/20, X-A/M series"},
  {cat:"Flash",        model:"EF-20",        desc:"Entry clip-on flash. GN20, TTL only (no manual). Draws from hotshoe.", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S, X-E1/2/3/4, X-S10/20, X-A/M series"},
  {cat:"Flash",        model:"EF-X8",        desc:"Tiny built-in-style clip flash. GN8, powered by camera. Covers 16mm (24mm FF).", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S"},
  {cat:"Flash",        model:"EF-W1",        desc:"Wireless commander. Controls EF-60 units via radio. Fits hotshoe, no flash output of its own.", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S, X-E1/2/3/4, X-S10/20, X-A/M series, GFX"},
  // Battery grips - current
  {cat:"Battery Grip", model:"VG-XT4",       desc:"Vertical grip for X-T4. Holds 2× NP-W235. WR. Adds portrait shutter, AF-ON, AE-L, command dials.", compat:"X-T4"},
  {cat:"Battery Grip", model:"VBG-XH",       desc:"Vertical grip for X-H2 / X-H2S. Holds 2× NP-W235. WR. Up to 1700 frames.", compat:"X-H2, X-H2S"},
  {cat:"Battery Grip", model:"VG-GFX100 II", desc:"Grip for GFX100 II. WR. Dramatically extends battery life for long studio or field sessions.", compat:"GFX100 II"},
  {cat:"Battery Grip", model:"FT-XH",        desc:"File Transmitter Battery Grip for X-H2S. Wired LAN + high-speed wireless. Holds 2× NP-W235.", compat:"X-H2S"},
  // Battery grips - legacy
  {cat:"Battery Grip", model:"VPB-XT2",      desc:"Power Booster Grip for X-T2. Holds 2× NP-W126S. WR. Adds 4K 4-stop boost, headphone jack, portrait controls. Popular for video.", compat:"X-T2"},
  {cat:"Battery Grip", model:"VG-XT1",       desc:"Vertical Battery Grip for X-T1. Holds 2× NP-W126S. WR. Portrait shutter and command dials.", compat:"X-T1"},
  {cat:"Battery Grip", model:"VG-XT3",       desc:"Vertical Battery Grip for X-T3. Holds 2× NP-W126S. WR.", compat:"X-T3"},
  {cat:"Hand Grip", model:"MHG-XT3",      desc:"Metal Hand Grip for X-T3. No extra battery — just improves ergonomics and adds Arca-Swiss rail mount.", compat:"X-T3"},
  {cat:"Hand Grip", model:"MHG-XT4",      desc:"Metal Hand Grip for X-T4. Improves grip, adds Arca-Swiss compatible rail. No extra battery.", compat:"X-T4"},
  {cat:"Hand Grip", model:"MHG-XT5",      desc:"Metal Hand Grip for X-T5. Improves grip, adds Arca-Swiss compatible rail. No extra battery.", compat:"X-T5"},
  {cat:"Hand Grip", model:"MHG-XH",       desc:"Metal Hand Grip for X-H2 / X-H2S. Arca-Swiss rail, improved ergonomics.", compat:"X-H2, X-H2S"},
  {cat:"Hand Grip", model:"MHG-XPRO2",    desc:"Metal Hand Grip for X-Pro2. Arca-Swiss rail, improves grip on the rangefinder-style body.", compat:"X-Pro2"},
  {cat:"Hand Grip", model:"MHG-XT10",     desc:"Metal Hand Grip for X-T10/X-T20. Improves grip, adds Arca-Swiss rail. Pairs with NP-W126S.", compat:"X-T10, X-T20"},
  {cat:"Hand Grip", model:"L-bracket (3rd party)", desc:"No official MHG exists for X-T1. Use a third-party Arca-Swiss L-bracket (Really Right Stuff, Kirk, Sunwayfoto) for tripod plate and portrait orientation mounting.", compat:"X-T1"},
  {cat:"Battery Grip", model:"VG-XPro1",     desc:"Vertical Battery Grip for X-Pro1. Holds 2× NP-W126. First Fuji X grip.", compat:"X-Pro1"},
  // Power - current
  {cat:"Power",        model:"NP-W126S",     desc:"Standard X-series Li-ion battery. Improved over NP-W126. ~350 frames. Compatible with most X-bodies.", compat:"X-T1/2/3, X-Pro1/2, X-E1/2/3, X-A, X-T10/20/30, X-T100"},
  {cat:"Power",        model:"NP-W235",      desc:"High-capacity Li-ion for newer flagships. ~680 frames (X-T5). Compatible with X-T4/5, X-H2/S, X-S20.", compat:"X-T4/5, X-H2/S, X-S20"},
  {cat:"Power",        model:"BC-W126S",     desc:"Single-slot charger for NP-W126S. Compact, travel-friendly.", compat:"NP-W126S battery"},
  {cat:"Power",        model:"EF-BP1",       desc:"External battery pack for EF-X500 flash. Takes 8× AA batteries for extended flash sessions.", compat:"EF-X500 flash"},
  // Power - legacy
  {cat:"Power",        model:"NP-W126",      desc:"Original X-series Li-ion battery. Replaced by NP-W126S but still compatible in all NP-W126S bodies. Widely available used.", compat:"X-T1/2/3, X-Pro1/2, X-E1/2/3, X-A, X-T10/20/30, X-T100, X-H1"},
  // Macro & Extension
  {cat:"Lens Accessory", model:"MCEX-11 WR", desc:"Extension tube 11mm. Increases macro magnification. WR. No AF when mounted (manual focus only).", compat:"XF 16/23/27/35/50/56/60/80/90mm, XF 10-24/16-55/16-80/50-140/100-400mm WR"},
  {cat:"Lens Accessory", model:"MCEX-16 WR", desc:"Extension tube 16mm. Greater magnification than MCEX-11. WR.", compat:"XF 16/23/27/35/50/56/60/80/90mm, XF 10-24/16-55/16-80/50-140/100-400mm WR"},
  {cat:"Lens Accessory", model:"MCEX-11",    desc:"Original non-WR extension tube 11mm. Works with all XF lenses. No autofocus.", compat:"All XF mount lenses (no weather sealing)"},
  {cat:"Lens Accessory", model:"MCEX-16",    desc:"Original non-WR extension tube 16mm. Works with all XF lenses. No autofocus.", compat:"All XF mount lenses (no weather sealing)"},
  {cat:"Lens Accessory", model:"MCEX-18G WR",desc:"Extension tube 18mm for G-Mount. WR.", compat:"All GF mount lenses"},
  {cat:"Lens Accessory", model:"MCEX-45G WR",desc:"Extension tube 45mm for G-Mount. WR. High magnification for macro work on GFX.", compat:"All GF mount lenses"},
  {cat:"Lens Accessory", model:"XF 1.4× TC WR", desc:"Tele converter 1.4×. 1 stop light loss. AF retained on compatible XF lenses.", compat:"XF 50-140, 100-400, 200mm, 70-300, 150-600"},
  {cat:"Lens Accessory", model:"XF 2.0× TC WR", desc:"Tele converter 2.0×. 2 stop light loss. AF retained on compatible XF lenses.", compat:"XF 50-140, 100-400, 200mm, 70-300, 150-600"},
  // Mount adapters
  {cat:"Adapter",      model:"M Mount Adapter", desc:"Allows Leica M-mount lenses on X-mount. Manual focus only. Covers a wide range of legacy glass.", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S, X-E1/2/3/4, X-S10/20, X-A/M series"},
  {cat:"Adapter",      model:"H Mount Adapter G", desc:"Allows older Fujifilm H-mount medium format lenses on GFX. Manual aperture control.", compat:"GFX 50S/50R/50S II/100/100S/100 II"},
  // Remote
  {cat:"Remote",       model:"RR-100",       desc:"Wired remote release. 2.5mm jack. Reduces camera shake for tripod work and time exposures.", compat:"X-T1/2/3/4/5, X-Pro1/2/3, X-H1/2/2S, GFX 50S/50R/100/100S/100 II"},
  {cat:"Remote",       model:"TG-BT1",       desc:"Bluetooth tripod grip. Controls shutter, video, power zoom lenses via Bluetooth from the grip.", compat:"X-T3/4/5, X-Pro3, X-H1/2/2S, X-E4, X-S10/20, X-100V/VI"},
  // Microphone
  {cat:"Audio",        model:"MIC-ST1",      desc:"Compact stereo microphone. Mounts on hotshoe, plugs into 3.5mm mic input. Improves video audio significantly.", compat:"X-T1/2/3/4, X-Pro1/2/3, X-H1/2/2S, X-E2/3/4, X-S10/20"},
  // Cooling
  {cat:"Body Accessory", model:"FAN-001",    desc:"Cooling fan for extended video recording. Prevents overheating during long 4K/6K sessions.", compat:"X-M5, X-H2S, X-H2, X-S20"},
  // Legacy body accessories
  {cat:"Body Accessory", model:"BLC-XT3",    desc:"Leather bottom case for X-T3. Luxurious protection, pictures can be taken with case on.", compat:"X-T3"},
  {cat:"Body Accessory", model:"BLC-XT2",    desc:"Leather bottom case for X-T2. Classic look, full access to battery/card slot.", compat:"X-T2"},
  {cat:"Body Accessory", model:"BLC-XT1",    desc:"Leather bottom case for X-T1. One of the most popular X accessories for the classic X-T1 aesthetic.", compat:"X-T1"},
  {cat:"Body Accessory", model:"LC-X100V",   desc:"Genuine leather case for X100V. Formfitting, improves grip, access to battery slot.", compat:"X100V"},
  {cat:"Body Accessory", model:"GB-001",     desc:"Grip belt add-on. Improves hand grip when combined with a hand grip accessory.", compat:"X-T1/2/3/4/5"},
  {cat:"Body Accessory", model:"CVR-XT3",    desc:"Cover set for X-T3. Protects connector covers from wear.", compat:"X-T3"},
];

function Accessories() {
  const cats = [...new Set(ACCESSORIES.map(a => a.cat))];
  const [activeCat, setActiveCat] = useState("All");
  const filtered = activeCat === "All" ? ACCESSORIES : ACCESSORIES.filter(a => a.cat === activeCat);

  return (
    <div>
      <div style={{display:"flex", gap:6, flexWrap:"wrap", marginBottom:14}}>
        {["All", ...cats].map(c => (
          <button key={c} className={`chip${activeCat===c?" on":""}`}
            onClick={() => setActiveCat(c)} style={{padding:"2px 8px"}}>{c}</button>
        ))}
      </div>
      <table style={{width:"100%", borderCollapse:"collapse"}}>
        <thead>
          <tr>
            <th style={{textAlign:"left", padding:"6px 10px", fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#8a8070", borderBottom:"1px solid #2a2520"}}>Model</th>
            <th style={{textAlign:"left", padding:"6px 10px", fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#8a8070", borderBottom:"1px solid #2a2520"}}>Category</th>
            <th style={{textAlign:"left", padding:"6px 10px", fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#8a8070", borderBottom:"1px solid #2a2520"}}>Description</th>
            <th style={{textAlign:"left", padding:"6px 10px", fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#8a8070", borderBottom:"1px solid #2a2520"}}>Compatible with</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(({cat, model, desc, compat}) => (
            <tr key={model} style={{borderBottom:"1px solid #1a1816"}}>
              <td style={{padding:"7px 10px", fontFamily:"'IBM Plex Mono',monospace", fontSize:11, color:"#e8a045", fontWeight:600, whiteSpace:"nowrap", maxWidth:120}}>{model}</td>
              <td style={{padding:"7px 10px", fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#b0a898", whiteSpace:"nowrap", background:"#141210", borderRight:"1px solid #2a2520"}}>{cat}</td>
              <td style={{padding:"7px 10px", fontFamily:"system-ui, sans-serif", fontSize:12, color:"#b0a898", lineHeight:1.5, maxWidth:300, wordWrap:"break-word", whiteSpace:"normal"}}>{desc}</td>
              <td style={{padding:"7px 10px", fontFamily:"'IBM Plex Mono',monospace", fontSize:10, color:"#6a6060", maxWidth:200}}>{compat}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── APP ──────────────────────────────────────────────────────────────────────
export default function Photography() {
  const [tab, setTab] = useState("lenses");

  return (
    <>
      <style>{css}</style>
      <div className="app">
        <div className="header">
          <h1>Fuji.me!</h1>
          <span className="sub">Lightweight · Fuji Screener · me! series · by <a href="https://braboj.me" target="_blank" rel="noopener noreferrer" style={{color:"inherit", textDecoration:"underline", opacity:0.7}}>braboj.me</a></span>
        </div>

        <div className="tabs">
          {[["lenses","Lens Explorer"],["camera","Camera Explorer"],["accessories","Accessories"],["trade","Trade Deals"],["ev","Genre Guide"],["glossary","Wiki"]].map(([v,l]) => (
            <button key={v} className={`tab${tab===v?" active":""}`} onClick={() => setTab(v)}>{l}</button>
          ))}
        </div>

        {tab === "lenses"  && <LensExplorer />}
        {tab === "camera"      && <CameraExplorer />}
        {tab === "accessories" && <Accessories />}
        {/* TODO: Calculator — Relative Exposure + Handheld shutter. Removed pending UX rework. See Calculator() below. */}
        {/* TODO: Recommendations/top labels — define criteria per genre before enabling.
            Confirmed: coma (astro), aperture, FL rule-of-500. Pending: vignetting, CA, field weight. */}
        {tab === "trade"   && <Trade />}
        {tab === "ev"      && <EVGuide />}
        {tab === "glossary" && <GlossaryView />}
      </div>
    </>
  );
}
