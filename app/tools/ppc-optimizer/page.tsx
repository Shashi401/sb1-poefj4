"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Upload, Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { ScrollArea } from "@/components/ui/scroll-area";
import * as XLSX from 'xlsx';

export default function PPCOptimizerPage() {
  const [data, setData] = useState<any[]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;

    const file = e.target.files[0];
    setIsLoading(true);
    setData([]);
    setHeaders([]);

    try {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const workbook = XLSX.read(event.target?.result, { type: 'binary' });
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);
          
          if (jsonData.length > 0) {
            setHeaders(Object.keys(jsonData[0]));
            setData(jsonData);
            toast({
              title: "File loaded successfully",
              description: `Loaded ${jsonData.length} rows of data`,
            });
          }
        } catch (error) {
          toast({
            title: "Error reading file",
            description: "Please ensure your file is a valid Excel file",
            variant: "destructive",
          });
        } finally {
          setIsLoading(false);
        }
      };

      reader.onerror = () => {
        toast({
          title: "Error reading file",
          description: "Failed to read the file",
          variant: "destructive",
        });
        setIsLoading(false);
      };

      reader.readAsBinaryString(file);
    } catch (error) {
      toast({
        title: "Error processing file",
        description: "An unexpected error occurred",
        variant: "destructive",
      });
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Excel File Viewer</CardTitle>
          <CardDescription>
            Upload your Excel file to view its contents
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="file">Excel File</Label>
              <Input
                id="file"
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileChange}
                className="cursor-pointer"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {(data.length > 0 || isLoading) && (
        <Card>
          <CardHeader>
            <CardTitle>File Contents</CardTitle>
            <CardDescription>
              Displaying data from your Excel file
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="rounded-md border h-[600px]">
              <Table>
                <TableHeader className="sticky top-0 bg-background">
                  <TableRow>
                    {headers.map((header, index) => (
                      <TableHead key={index} className="min-w-[150px]">
                        {header}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {isLoading ? (
                    <TableRow>
                      <TableCell colSpan={headers.length} className="text-center h-24">
                        <Loader2 className="h-6 w-6 animate-spin mx-auto" />
                        <span className="text-sm text-muted-foreground">Loading data...</span>
                      </TableCell>
                    </TableRow>
                  ) : data.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={headers.length} className="text-center h-24">
                        <span className="text-sm text-muted-foreground">No data available</span>
                      </TableCell>
                    </TableRow>
                  ) : (
                    data.map((row, index) => (
                      <TableRow key={index}>
                        {headers.map((header, cellIndex) => (
                          <TableCell key={cellIndex}>
                            {row[header]?.toString() || ''}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}