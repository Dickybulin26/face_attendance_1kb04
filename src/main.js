import "./style.css";
import {
  createIcons,
  ShieldCheck,
  ScanFace,
  History,
  Users,
  UserPlus,
  LogOut,
  Search,
  Code2,
  PlusSquare,
  Fingerprint,
  Edit,
  Save,
  Trash,
  AlertOctagon,
  X,
  Calendar as CalendarIcon,
  Rss,
  Info,
  Filter,
  CheckCircle,
  ArrowRight,
  Plus,
} from "lucide";
import Swal from "sweetalert2";
import { Calendar } from "@fullcalendar/core";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { FaceDetection } from "@mediapipe/face_detection";
import { Camera } from "@mediapipe/camera_utils";

// Assign global variables to window so inline HTML scripts can access them
window.Swal = Swal;
window.FaceDetection = FaceDetection;
window.Camera = Camera;
window.FullCalendar = { Calendar }; // Mock FullCalendar global for existing code
window.dayGridPlugin = dayGridPlugin;
window.interactionPlugin = interactionPlugin;

// Setup Lucide
window.lucide = {
  createIcons: () => {
    createIcons({
      icons: {
        ShieldCheck,
        ScanFace,
        History,
        Users,
        UserPlus,
        LogOut,
        Search,
        Code2,
        PlusSquare,
        Fingerprint,
        Edit,
        Save,
        Trash,
        AlertOctagon,
        X,
        Calendar: CalendarIcon,
        Rss,
        Info,
        Filter,
        CheckCircle,
        ArrowRight,
        Plus,
      },
    });
  },
};

// Import main application logic
import "./app.js";
