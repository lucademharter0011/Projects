import { useSession } from "next-auth/react";
import { Button } from "./ui/button";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { useCallback, useEffect, useState } from "react";
import { Course, Timetable } from "@/types";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Plus, Trash } from "lucide-react";

type AppHeaderProps = {
  selectedTimetable: number | null;
  onSelectTimetable: (id: number | null) => void;
};

export default function TimetableHeader({
  onSelectTimetable,
  selectedTimetable,
}: AppHeaderProps) {
  const { data: session, status } = useSession();
  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number | "">("");
  const [newName, setNewName] = useState("");
  const [loading, setLoading] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const token = session?.user.accessToken ?? "";

  const fetchTimetables = useCallback(async () => {
    if (!token) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/timetable/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      const data = await response.json();
      setTimetables(data.timetables || []);
    } catch (error) {
      console.error("Failed to fetch timetables:", error);
    }
  }, [token]);

  const fetchCourses = useCallback(async () => {
    if (!token) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/courses/catalog`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      const data = await response.json();
      setCourses(data.courses || []);
    } catch (error) {
      console.error("Failed to fetch courses:", error);
    }
  }, [token]);

  useEffect(() => {
    if (status !== "authenticated") return;

    fetchTimetables();
    fetchCourses();
  }, [status, fetchTimetables, fetchCourses]);

  const handleCreate = async () => {
    if (!newName.trim() || !token) return;

    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/timetable/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newName, is_active: true }),
      });
      if (!res.ok) throw new Error(await res.text());
      const { timetable } = await res.json();
      setTimetables((prev) => [...prev, timetable]);
      onSelectTimetable(timetable.id);
      setNewName("");
      setCreateDialogOpen(false);
    } catch (err) {
      console.error("Could not create timetable:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedTimetable) return;

    setDeleteLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/timetable/${selectedTimetable}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }

      setTimetables((prev) => prev.filter((t) => t.id !== selectedTimetable));

      // If we deleted the selected timetable, select the first remaining one
      const remainingTimetables = timetables.filter(
        (t) => t.id !== selectedTimetable
      );
      if (remainingTimetables.length > 0) {
        onSelectTimetable(remainingTimetables[0].id);
      } else {
        onSelectTimetable(null);
      }

      setDeleteDialogOpen(false);
    } catch (err) {
      console.error("Could not delete timetable:", err);
    } finally {
      setDeleteLoading(false);
    }
  };

  const selectedTimetableName = timetables.find(
    (t) => t.id === selectedTimetable
  )?.name;

  return (
    <header>
      <div className="font-medium py-3 text-foreground flex justify-between flex-wrap gap-4">
        <div className="flex gap-2">
          <Select
            value={selectedTimetable?.toString() || ""}
            onValueChange={(val) => onSelectTimetable(Number(val))}
          >
            <SelectTrigger className="placeholder:text-black text-base text-black bg-transparent border-border">
              <SelectValue placeholder="Stundenplan" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Stundenpläne</SelectLabel>
                {timetables.map((timetable) => (
                  <SelectItem
                    key={timetable.id}
                    value={timetable.id.toString()}
                    className="cursor-pointer"
                  >
                    {timetable.name}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>

          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button
                aria-label="Neuen Stundenplan hinzufügen"
                size="icon"
                variant="outline"
              >
                <Plus />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Neuen Stundenplan erstellen</DialogTitle>
                <DialogDescription>
                  Gib deinem neuen Stundenplan einen Namen.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-2">
                <Label htmlFor="new-timetable-name">Name</Label>
                <Input
                  id="new-timetable-name"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="z.B. Wintersemester 24/25"
                />
              </div>
              <DialogFooter className="mt-4 flex justify-end space-x-2">
                <DialogClose asChild>
                  <Button variant="ghost" disabled={loading}>
                    Abbrechen
                  </Button>
                </DialogClose>
                <Button
                  onClick={handleCreate}
                  disabled={!newName.trim() || loading}
                >
                  {loading ? <span className="loading"></span> : "Erstellen"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                disabled={!selectedTimetable || timetables.length <= 1}
                size="icon"
                aria-label="Aktuellen Stundenplan löschen"
              >
                <Trash />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Stundenplan löschen</DialogTitle>
                <DialogDescription>
                  Möchten Sie den Stundenplan &quot;{selectedTimetableName}
                  &quot; wirklich löschen? Diese Aktion kann nicht rückgängig
                  gemacht werden.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter className="mt-4 flex justify-end space-x-2">
                <DialogClose asChild>
                  <Button variant="ghost" disabled={deleteLoading}>
                    Abbrechen
                  </Button>
                </DialogClose>
                <Button
                  onClick={handleDelete}
                  disabled={deleteLoading}
                  variant="destructive"
                >
                  {deleteLoading ? "…" : "Löschen"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button disabled={!selectedTimetable} variant="outline">
              Kurs hinzufügen
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Kurs hinzufügen</DialogTitle>
              <DialogDescription>
                Wählen Sie einen Kurs aus, um ihn zu Ihrem Stundenplan
                hinzuzufügen. Hinzufügen funktioniert nicht.
              </DialogDescription>
              <Select
                value={selectedCourseId.toString()}
                onValueChange={(v) => setSelectedCourseId(Number(v))}
              >
                <SelectTrigger className="w-full mt-4">
                  <SelectValue placeholder="Kurs auswählen" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Kurse</SelectLabel>
                    {courses.map((course) => (
                      <SelectItem key={course.id} value={course.id.toString()}>
                        {course.name} ({course.code})
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </DialogHeader>
            <DialogFooter>
              <DialogClose asChild>
                <Button>Hinzufügen</Button>
              </DialogClose>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </header>
  );
}
